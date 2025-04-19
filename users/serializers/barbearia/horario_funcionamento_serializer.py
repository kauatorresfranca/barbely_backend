from rest_framework import serializers
from users.models import HorarioFuncionamento

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
