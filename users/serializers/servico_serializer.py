from rest_framework import serializers
from users.models.servico import Servico

class ServicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servico
        fields = ['id', 'barbearia', 'nome', 'preco', 'duracao_minutos']
        read_only_fields = ['barbearia']

    def validate_nome(self, value):
        barbearia = self.context['request'].user
        if Servico.objects.filter(barbearia=barbearia, nome=value).exists():
            raise serializers.ValidationError("Já existe um serviço com esse nome.")
        return value
