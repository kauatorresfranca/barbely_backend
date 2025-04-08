from rest_framework import serializers
from ..models.agendamento import Agendamento, Servico, Funcionario
from datetime import timedelta

class AgendamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agendamento
        fields = ['id', 'cliente', 'funcionario', 'servico', 'hora_inicio', 'cancelado', 'criado_em']
        read_only_fields = ['cliente', 'cancelado', 'criado_em']

    def validate(self, data):
        funcionario = data['funcionario']
        servico = data['servico']
        hora_inicio = data['hora_inicio']
        hora_fim = hora_inicio + timedelta(minutes=servico.duracao_minutos)

        conflitos = Agendamento.objects.filter(
            funcionario=funcionario,
            cancelado=False,
            hora_inicio__lt=hora_fim,
            hora_inicio__gte=hora_inicio - timedelta(minutes=servico.duracao_minutos)
        )

        if conflitos.exists():
            raise serializers.ValidationError("Esse horário já está ocupado para o funcionário selecionado.")

        return data

