from rest_framework import serializers
from ..models.barbearia import Barbearia

class BarbeariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Barbearia
        fields = [
            'id', 'nome_barbearia', 'nome_proprietario', 'email', 'username', 'password', 'cnpj', 'plano', 'data_criacao'
        ]
        extra_kwargs = {
            'password': {'write_only': True},  # Não retorna a senha na resposta
            'username': {'required': False},
        }

    def create(self, validated_data):
        # Geração automática do username se não for fornecido
        if 'username' not in validated_data or not validated_data['username']:
            base_username = validated_data['nome_proprietario'].lower().replace(" ", "_")
            contador = 1
            new_username = base_username

            # Garante que o username seja único no banco
            while Barbearia.objects.filter(username=new_username).exists():
                new_username = f"{base_username}_{contador}"
                contador += 1

            validated_data['username'] = new_username

        # Criação do usuário e criptografia da senha
        senha_plana = validated_data.pop("password", None)
        barbearia = Barbearia(**validated_data)
        if senha_plana:
            barbearia.set_password(senha_plana)  # Criptografa a senha
        barbearia.save()
        return barbearia
