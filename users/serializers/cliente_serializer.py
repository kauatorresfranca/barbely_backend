from rest_framework import serializers
from users.models import Cliente, ClienteUser
import logging

logger = logging.getLogger(__name__)

class ClienteUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClienteUser
        fields = ['email', 'nome', 'telefone', 'password']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'email': {'required': False},
            'nome': {'required': False},
            'telefone': {'required': False},
        }

    def validate_telefone(self, value):
        import re
        if value and not re.match(r'^\(\d{2}\) \d{5}-\d{4}$', value):
            raise serializers.ValidationError("Telefone deve estar no formato (XX) XXXXX-XXXX.")
        return value

    def validate(self, data):
        logger.debug(f"Validating user data: {data}")
        if self.instance:  # Atualização
            email = data.get('email', self.instance.email)
            telefone = data.get('telefone', self.instance.telefone)
            # Ignorar validação de unicidade se o email não mudou
            if email != self.instance.email and ClienteUser.objects.filter(email=email).exists():
                raise serializers.ValidationError({"email": "Cliente user with this email already exists."})
            if telefone != self.instance.telefone and ClienteUser.objects.filter(telefone=telefone).exists():
                raise serializers.ValidationError({"telefone": "Cliente user with this telefone already exists."})
        return data

class ClienteSerializer(serializers.ModelSerializer):
    user = ClienteUserSerializer(partial=True)

    class Meta:
        model = Cliente
        fields = ['id', 'user', 'barbearia', 'imagem']
        extra_kwargs = {
            'barbearia': {'required': True},
            'imagem': {'required': False},
        }

    def validate_imagem(self, value):
        logger.debug(f"Validating imagem: {value}")
        if value:
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("A imagem não pode exceder 5MB.")
            if not value.content_type.startswith('image/'):
                raise serializers.ValidationError("O arquivo deve ser uma imagem válida.")
        return value

    def validate(self, data):
        logger.debug(f"Validating data: {data}")
        return data

    def create(self, validated_data):
        logger.debug(f"Creating cliente with data: {validated_data}")
        user_data = validated_data.pop('user')
        password = user_data.pop('password', None)
        user = ClienteUser.objects.create(**user_data)
        if password:
            user.set_password(password)
            user.save()
        cliente = Cliente.objects.create(user=user, **validated_data)
        return cliente

    def update(self, instance, validated_data):
        logger.debug(f"Updating cliente with validated data: {validated_data}")
        user_data = validated_data.pop('user', None)
        if user_data:
            logger.debug(f"Updating user with data: {user_data}")
            user_serializer = ClienteUserSerializer(instance.user, data=user_data, partial=True)
            if user_serializer.is_valid(raise_exception=True):
                user_serializer.save()

        for attr, value in validated_data.items():
            logger.debug(f"Setting {attr} = {value}")
            setattr(instance, attr, value)
        instance.save()
        logger.debug(f"Updated instance: {instance.__dict__}")
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['fotoPerfil'] = instance.imagem.url if instance.imagem else None
        logger.debug(f"Returning representation: {representation}")
        return representation