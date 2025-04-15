from rest_framework import serializers
from users.models.agendamento import Agendamento, Servico, Funcionario
from datetime import timedelta
from datetime import datetime, timedelta

class AgendamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agendamento
        fields = ['id', 'cliente', 'funcionario', 'servico', 'data', 'hora_inicio', 'cancelado', 'criado_em']
        read_only_fields = ['cliente', 'cancelado', 'criado_em']

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

        conflitos = Agendamento.objects.filter(
            funcionario=funcionario,
            cancelado=False,
            data=data_agendamento,
        ).exclude(
            hora_inicio__gte=datetime_fim.time()
        ).exclude(
            hora_inicio__lt=hora_inicio
        )

        if conflitos.exists():
            raise serializers.ValidationError("Esse horário já está ocupado para o funcionário selecionado.")

        return data

