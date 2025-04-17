from rest_framework import serializers
from users.models import Agendamento, Servico, Funcionario
from datetime import datetime, timedelta

class AgendamentoSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.CharField(source='cliente.nome', read_only=True)
    servico_nome = serializers.CharField(source='servico.nome', read_only=True)
    servico_duracao = serializers.IntegerField(source='servico.duracao_minutos', read_only=True)

    class Meta:
        model = Agendamento
        fields = [
            'id', 'cliente', 'cliente_nome', 'funcionario', 'servico',
            'servico_nome', 'servico_duracao', 'data', 'hora_inicio',
            'status', 'criado_em'
        ]
        read_only_fields = ['id', 'cliente', 'cliente_nome', 'servico_nome', 'servico_duracao', 'status', 'criado_em']

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