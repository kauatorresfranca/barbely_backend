from rest_framework import serializers
from users.models import Cliente, ClienteUser

class ClienteUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClienteUser
        fields = ['email', 'nome', 'telefone', 'password']
        extra_kwargs = {'password': {'write_only': True}}

class ClienteSerializer(serializers.ModelSerializer):
    user = ClienteUserSerializer()

    class Meta:
        model = Cliente
        fields = ['id', 'user', 'nome', 'telefone', 'barbearia']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        password = user_data.pop('password')
        user = ClienteUser.objects.create(**user_data)
        user.set_password(password)
        user.save()

        cliente = Cliente.objects.create(user=user, **validated_data)
        return cliente
