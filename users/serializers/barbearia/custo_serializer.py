from rest_framework import serializers
from users.models.custo import Custo

class CustoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Custo
        fields = ['id', 'descricao', 'valor', 'data', 'tipo']
        extra_kwargs = {
            'barbearia': {'write_only': True},
        }