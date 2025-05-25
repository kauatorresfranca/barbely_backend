# users/serializers/funcionario_serializer.py
from rest_framework import serializers
from users.models import Funcionario, Agendamento
from users.serializers.agendamento_serializer import AgendamentoSerializer
import logging
from django.utils import timezone
from django.db.models import Sum  # Add this import

logger = logging.getLogger(__name__)

class FuncionarioSerializer(serializers.ModelSerializer):
    fotoPerfil = serializers.SerializerMethodField()
    historico = serializers.SerializerMethodField()
    estatisticas = serializers.SerializerMethodField()
    total_servicos = serializers.SerializerMethodField()

    class Meta:
        model = Funcionario
        fields = ['id', 'barbearia', 'nome', 'email', 'telefone', 'imagem', 'fotoPerfil', 'historico', 'estatisticas', 'total_servicos']
        read_only_fields = ['barbearia']
        extra_kwargs = {
            'imagem': {'required': False},
            'email': {'required': False},
            'telefone': {'required': False},
        }

    def get_fotoPerfil(self, obj):
        if obj.imagem and hasattr(obj.imagem, 'url'):
            return obj.imagem.url
        return None

    def get_historico(self, obj):
        agendamentos = Agendamento.objects.filter(funcionario=obj, status__in=['CONFIRMADO', 'CONCLUIDO']).order_by('-data', '-hora_inicio')[:5]
        return AgendamentoSerializer(agendamentos, many=True).data

    def get_estatisticas(self, obj):
        hoje = timezone.now().date()
        inicio_mes = hoje.replace(day=1)

        # Agendamentos este mês
        agendamentos_mes = Agendamento.objects.filter(
            funcionario=obj,
            data__gte=inicio_mes,
            status__in=['CONFIRMADO', 'CONCLUIDO']
        ).count()

        # Total de agendamentos
        total_agendamentos = Agendamento.objects.filter(
            funcionario=obj,
            status__in=['CONFIRMADO', 'CONCLUIDO']
        ).count()

        # Receita gerada
        receita_total = Agendamento.objects.filter(
            funcionario=obj,
            status__in=['CONFIRMADO', 'CONCLUIDO']
        ).aggregate(total=Sum('preco_total'))['total'] or 0  # Use Sum directly

        # Cliente mais frequente
        cliente_mais_frequente = Agendamento.objects.filter(
            funcionario=obj,
            status__in=['CONFIRMADO', 'CONCLUIDO']
        ).values('cliente__user__nome').annotate(count=Sum('id')).order_by('-count').first()
        cliente_mais_frequente_nome = cliente_mais_frequente['cliente__user__nome'] if cliente_mais_frequente else 'Nenhum'

        # Serviço mais realizado
        servico_mais_realizado = Agendamento.objects.filter(
            funcionario=obj,
            status__in=['CONFIRMADO', 'CONCLUIDO']
        ).values('servico__nome').annotate(count=Sum('id')).order_by('-count').first()
        servico_mais_realizado_nome = servico_mais_realizado['servico__nome'] if servico_mais_realizado else 'Nenhum'

        return {
            'agendamentos_este_mes': agendamentos_mes,
            'total_agendamentos': total_agendamentos,
            'receita_total': f"R$ {receita_total:.2f}",
            'cliente_mais_frequente': cliente_mais_frequente_nome,
            'servico_mais_realizado': servico_mais_realizado_nome,
        }

    def get_total_servicos(self, obj):
        return Agendamento.objects.filter(funcionario=obj, status__in=['CONFIRMADO', 'CONCLUIDO']).count()

    def validate_nome(self, value):
        barbearia = self.context['request'].user
        if self.instance:
            if Funcionario.objects.filter(barbearia=barbearia, nome=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Já existe um funcionário com esse nome.")
        else:
            if Funcionario.objects.filter(barbearia=barbearia, nome=value).exists():
                raise serializers.ValidationError("Já existe um funcionário com esse nome.")
        return value

    def validate_email(self, value):
        if value:
            barbearia = self.context['request'].user
            if self.instance:
                if Funcionario.objects.filter(barbearia=barbearia, email=value).exclude(id=self.instance.id).exists():
                    raise serializers.ValidationError("Já existe um funcionário com esse email.")
            else:
                if Funcionario.objects.filter(barbearia=barbearia, email=value).exists():
                    raise serializers.ValidationError("Já existe um funcionário com esse email.")
        return value

    def validate_telefone(self, value):
        if value:
            if not value.replace(' ', '').replace('-', '').replace('(', '').replace(')', '').isdigit():
                raise serializers.ValidationError("O telefone deve conter apenas números, espaços, parênteses ou hífens.")
            if len(value) < 10 or len(value) > 15:
                raise serializers.ValidationError("O telefone deve ter entre 10 e 15 caracteres.")
        return value

    def validate_imagem(self, value):
        logger.debug(f"Validating imagem: {value}")
        if value:
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("A imagem não pode exceder 5MB.")
            if not value.content_type.startswith('image/'):
                raise serializers.ValidationError("O arquivo deve ser uma imagem válida.")
        return value

    def validate(self, data):
        logger.debug(f"Validating data: {data}")
        return data