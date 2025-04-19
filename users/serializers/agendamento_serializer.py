from rest_framework import serializers
from users.models import Agendamento
from datetime import datetime, timedelta

class AgendamentoSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.SerializerMethodField()
    servico_nome = serializers.SerializerMethodField()
    servico_duracao = serializers.SerializerMethodField()

    class Meta:
        model = Agendamento
        fields = [
            'id', 'cliente', 'cliente_nome', 'funcionario', 'servico',
            'servico_nome', 'servico_duracao', 'data', 'hora_inicio',
            'status', 'criado_em'
        ]
        read_only_fields = ['id', 'cliente', 'cliente_nome', 'servico_nome', 'servico_duracao', 'status', 'criado_em']

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
        funcionario = data['funcionario']
        servico = data['servico']
        hora_inicio = data['hora_inicio']
        data_agendamento = data.get('data')

        if not data_agendamento:
            raise serializers.ValidationError("A data do agendamento é obrigatória.")

        # Combina data + hora_inicio
        datetime_inicio = datetime.combine(data_agendamento, hora_inicio)
        datetime_fim = datetime_inicio + timedelta(minutes=servico.duracao_minutos)

        # Verifica conflitos de horário
        conflitos = Agendamento.objects.filter(
            funcionario=funcionario,
            status__in=['CONFIRMADO', 'CONCLUIDO'],
            data=data_agendamento,
        ).exclude(
            hora_inicio__gte=datetime_fim.time()
        ).exclude(
            hora_inicio__lt=hora_inicio
        )

        if conflitos.exists():
            raise serializers.ValidationError("Esse horário já está ocupado para o funcionário selecionado.")

        return data