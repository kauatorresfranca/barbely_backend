from rest_framework import serializers
from users.models import Barbearia

class BarbeariaUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Barbearia
        fields = [
            'nome_barbearia',
            'nome_proprietario',
            'cnpj',
            'cpf',
            'telefone',
            'descricao',
            'imagem',
            'slug',        # ← agora editável
            'username',    # ← agora editável
        ]
