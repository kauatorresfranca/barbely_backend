from rest_framework import serializers
from users.models import Agendamento, HorarioFuncionamento
from datetime import datetime, timedelta
from django.utils import timezone
import logging

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
    servico_nome = serializers.SerializerMethodField()
    servico_duracao = serializers.SerializerMethodField()

    class Meta:
        model = Agendamento
        fields = [
            'id', 'cliente', 'cliente_nome', 'funcionario', 'servico',
            'servico_nome', 'servico_duracao', 'data', 'hora_inicio',
            'status', 'criado_em', 'preco_total'
        ]
        read_only_fields = ['id', 'cliente_nome', 'servico_nome', 'servico_duracao', 'criado_em', 'preco_total']

    def get_cliente_nome(self, obj):
        try:
            if obj.cliente and obj.cliente.user:
                return obj.cliente.user.nome or "Nome não disponível"
            return "Cliente não disponível"
        except Exception as e:
            return f"Erro ao acessar nome do cliente: {str(e)}"

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

        required_fields = ['cliente', 'funcionario', 'servico', 'hora_inicio', 'data']
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

        if funcionario.barbearia != barbearia:
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