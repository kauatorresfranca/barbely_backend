from rest_framework import serializers
from users.models import Barbearia

class BarbeariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Barbearia
        fields = [
            'id', 'nome_barbearia', 'nome_proprietario', 'email', 'username',
            'password', 'cnpj', 'plano', 'data_criacao', 'slug',
        ]
        extra_kwargs = {
            'password': {'write_only': True}, 
            'username': {'required': False},
        }

    def create(self, validated_data):
        # Gerando username automaticamente se não for fornecido
        if not validated_data.get('username'):
            base_username = validated_data['nome_proprietario'].lower().replace(" ", "_")
            contador = 1
            new_username = base_username

            while Barbearia.objects.filter(username=new_username).exists():
                new_username = f"{base_username}_{contador}"
                contador += 1

            validated_data['username'] = new_username

        # Criando o usuário com senha criptografada
        senha_plana = validated_data.pop("password", None)
        barbearia = Barbearia(**validated_data)
        if senha_plana:
            barbearia.set_password(senha_plana)  # ✅ Senha criptografada corretamente
        barbearia.save()
        return barbearia
