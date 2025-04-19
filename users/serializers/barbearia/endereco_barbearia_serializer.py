from rest_framework import serializers
from users.models.barbearia.endereco_barbearia import EnderecoBarbearia

class EnderecoBarbeariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnderecoBarbearia
        fields = '__all__'
        read_only_fields = ['barbearia']  # 🔒 Isso impede envio manual do campo

