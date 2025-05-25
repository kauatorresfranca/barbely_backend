from rest_framework import serializers
from users.models import Agendamento, HorarioFuncionamento, Cliente, Servico
from users.models.cliente.cliente_user import ClienteUser
from django.db import transaction
from datetime import datetime, timedelta
from django.utils import timezone
import logging
from users.utils.utils import generate_random_password

logger = logging.getLogger(__name__)

class HorarioFuncionamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HorarioFuncionamento
        fields = ['id', 'dia_semana', 'horario_abertura', 'horario_fechamento', 'fechado', 'barbearia']
        extra_kwargs = {
            'barbearia': {'read_only': True},
        }

    def validate(self, data):
        fechado = data.get("fechado", False)
        abertura = data.get("horario_abertura")
        fechamento = data.get("horario_fechamento")

        if not fechado:
            if abertura is None or fechamento is None:
                raise serializers.ValidationError("Horário de abertura e fechamento são obrigatórios se o dia não estiver marcado como fechado.")
            if abertura >= fechamento:
                raise serializers.ValidationError("A hora de abertura deve ser antes da hora de fechamento.")
        return data

class AgendamentoSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.SerializerMethodField()
    funcionario_nome = serializers.SerializerMethodField()  # Adicionado
    servico_nome = serializers.SerializerMethodField()
    servico_duracao = serializers.SerializerMethodField()
    metodo_pagamento = serializers.CharField(allow_null=True)
    hora_inicio = serializers.TimeField(required=True)
    cliente = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all(), write_only=True)

    class Meta:
        model = Agendamento
        fields = [
            'id', 'cliente', 'cliente_nome', 'funcionario', 'funcionario_nome', 'servico',
            'servico_nome', 'servico_duracao', 'data', 'hora_inicio',
            'status', 'criado_em', 'preco_total', 'metodo_pagamento'
        ]
        read_only_fields = ['id', 'cliente_nome', 'funcionario_nome', 'servico_nome', 'servico_duracao', 'criado_em', 'preco_total']

    def get_cliente_nome(self, obj):
        try:
            if obj.cliente and obj.cliente.user:
                return obj.cliente.user.nome or "Nome não disponível"
            return "Cliente não disponível"
        except Exception as e:
            return f"Erro ao acessar nome do cliente: {str(e)}"

    def get_funcionario_nome(self, obj):
        try:
            if obj.funcionario:
                return obj.funcionario.nome or "Funcionário não disponível"
            return "Sem preferência"
        except Exception as e:
            return f"Erro ao acessar nome do funcionário: {str(e)}"

    def get_servico_nome(self, obj):
        try:
            if obj.servico:
                return obj.servico.nome or "Serviço não disponível"
            return "Serviço não disponível"
        except Exception as e:
            return f"Erro ao acessar nome do serviço: {str(e)}"

    def get_servico_duracao(self, obj):
        try:
            if obj.servico:
                return obj.servico.duracao_minutos or 0
            return 0
        except Exception as e:
            return f"Erro ao acessar duração do serviço: {str(e)}"

    def validate(self, data):
        if self.context['request'].method == 'PATCH' and 'status' in data:
            return data

        required_fields = ['funcionario', 'servico', 'data', 'hora_inicio', 'cliente']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise serializers.ValidationError(
                f"Os seguintes campos são obrigatórios: {', '.join(missing_fields)}"
            )

        funcionario = data['funcionario']
        servico = data['servico']
        hora_inicio = data['hora_inicio']
        data_agendamento = data['data']
        barbearia = servico.barbearia

        if funcionario and funcionario.barbearia != barbearia:
            raise serializers.ValidationError(
                "O funcionário selecionado não pertence à barbearia do serviço."
            )

        try:
            horario = HorarioFuncionamento.objects.get(
                barbearia=barbearia,
                dia_semana=data_agendamento.weekday()
            )
            if horario.fechado:
                raise serializers.ValidationError(
                    "A barbearia está fechada neste dia."
                )
            hora_fechamento_ajustada = (datetime.combine(data_agendamento, horario.horario_fechamento) -
                                       timedelta(minutes=servico.duracao_minutos)).time()
            if not (horario.horario_abertura <= hora_inicio <= hora_fechamento_ajustada):
                raise serializers.ValidationError(
                    f"O horário {hora_inicio.strftime('%H:%M')} está fora do horário de funcionamento da barbearia."
                )
        except HorarioFuncionamento.DoesNotExist:
            raise serializers.ValidationError(
                "Horário de funcionamento não definido para este dia."
            )

        datetime_inicio = datetime.combine(data_agendamento, hora_inicio)
        datetime_inicio = timezone.make_aware(datetime_inicio, timezone.get_current_timezone())
        datetime_fim = datetime_inicio + timedelta(minutes=servico.duracao_minutos)

        conflitos = Agendamento.objects.filter(
            funcionario=funcionario,
            data=data_agendamento,
            status__in=['CONFIRMADO', 'CONCLUIDO'],
        ).exclude(id=self.instance.id if self.instance else None)

        for agendamento in conflitos:
            existing_inicio = datetime.combine(data_agendamento, agendamento.hora_inicio)
            existing_inicio = timezone.make_aware(existing_inicio, timezone.get_current_timezone())
            existing_fim = existing_inicio + timedelta(minutes=agendamento.servico.duracao_minutos)

            if not (datetime_fim <= existing_inicio or datetime_inicio >= existing_fim):
                logger.error(
                    f"Conflito detectado: Novo agendamento ({datetime_inicio} - {datetime_fim}) "
                    f"conflita com agendamento {agendamento.id} ({existing_inicio} - {existing_fim})"
                )
                raise serializers.ValidationError(
                    "Esse horário já está ocupado para o funcionário selecionado."
                )

        return data

class CriarAgendamentoSerializer(AgendamentoSerializer):
    cliente_email = serializers.EmailField(write_only=True, required=False, allow_blank=True)
    cliente_nome = serializers.CharField(write_only=True, max_length=255, required=False, allow_blank=True)
    metodo_pagamento = serializers.CharField(write_only=True)
    hora_inicio = serializers.TimeField(write_only=True, required=True)

    class Meta(AgendamentoSerializer.Meta):
        fields = AgendamentoSerializer.Meta.fields + ['cliente_email', 'cliente_nome', 'metodo_pagamento']

    def validate(self, data):
        data = super().validate(data)
        metodo_pagamento = data.get('metodo_pagamento')
        if not metodo_pagamento:
            raise serializers.ValidationError({
                'metodo_pagamento': 'O método de pagamento é obrigatório.'
            })
        metodo_pagamento_map = {
            'PIX': 'pix',
            'Cartão de Crédito': 'cartao_credito',
            'Cartão de Débito': 'cartao_debito',
            'Dinheiro': 'dinheiro'
        }
        if metodo_pagamento not in metodo_pagamento_map:
            valid_methods = list(metodo_pagamento_map.keys())
            raise serializers.ValidationError({
                'metodo_pagamento': f"Método de pagamento inválido. Opções válidas: {', '.join(valid_methods)}"
            })
        data['metodo_pagamento'] = metodo_pagamento_map[metodo_pagamento]
        return data

    def create(self, validated_data):
        cliente_email = validated_data.pop('cliente_email', None)
        cliente_nome = validated_data.pop('cliente_nome', None)
        metodo_pagamento = validated_data.pop('metodo_pagamento')
        barbearia = validated_data['servico'].barbearia
        hora_inicio = validated_data.pop('hora_inicio')

        with transaction.atomic():
            try:
                if 'cliente' not in validated_data:
                    cliente_user = self.context['request'].user
                    cliente = Cliente.objects.get(user=cliente_user, barbearia=barbearia)
                else:
                    cliente = validated_data['cliente']
                
                if cliente_email and cliente_nome:
                    cliente_user = ClienteUser.objects.get(email=cliente_email)
                    if cliente_nome and cliente.user.nome != cliente_nome:
                        cliente.user.nome = cliente_nome
                        cliente.user.save()
            except ClienteUser.DoesNotExist:
                cliente_user = ClienteUser.objects.create_user(
                    email=cliente_email or f"temp_{generate_random_password(8)}@example.com",
                    nome=cliente_nome or "Cliente sem nome",
                    password=generate_random_password()
                )
                cliente = Cliente.objects.create(
                    user=cliente_user,
                    barbearia=barbearia
                )
            except Cliente.DoesNotExist:
                cliente = Cliente.objects.create(
                    user=cliente_user,
                    barbearia=barbearia
                )

            validated_data['cliente'] = cliente
            validated_data['hora_inicio'] = hora_inicio

            agendamento = Agendamento.objects.create(
                metodo_pagamento=metodo_pagamento,
                preco_total=validated_data['servico'].preco,
                **validated_data
            )
            logger.debug(f"Agendamento criado: ID {agendamento.id} para cliente {cliente_email or cliente_user.email}")
            return agendamento