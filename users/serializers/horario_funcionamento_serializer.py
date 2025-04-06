from rest_framework import serializers
from users.models import HorarioFuncionamento

class HorarioFuncionamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HorarioFuncionamento
        fields = ['id', 'dia_semana', 'horario_abertura', 'horario_fechamento', 'barbearia']
        extra_kwargs = {
            'barbearia': {'read_only': True},
        }

    def validate(self, data):
        abertura = data.get("horario_abertura")
        fechamento = data.get("horario_fechamento")

        if abertura and fechamento and abertura >= fechamento:
            raise serializers.ValidationError("A hora de abertura deve ser antes da hora de fechamento.")

        return data
