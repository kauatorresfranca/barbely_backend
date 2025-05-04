from rest_framework import serializers
from users.models import Cliente, ClienteUser
import logging
from rest_framework_simplejwt.tokens import RefreshToken

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
            # Obter os valores atuais da instância
            current_email = self.instance.email
            current_telefone = self.instance.telefone

            # Verificar se o email foi fornecido e se mudou
            email = data.get('email')
            if email is not None and email != current_email:
                if ClienteUser.objects.exclude(id=self.instance.id).filter(email=email).exists():
                    raise serializers.ValidationError({"email": "Cliente user with this email already exists."})

            # Verificar se o telefone foi fornecido e se mudou
            telefone = data.get('telefone')
            if telefone is not None and telefone != current_telefone:
                if ClienteUser.objects.exclude(id=self.instance.id).filter(telefone=telefone).exists():
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

class ClienteLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        try:
            user = ClienteUser.objects.get(email=email)
        except ClienteUser.DoesNotExist:
            raise serializers.ValidationError("Usuário não encontrado.")

        if not user.check_password(password):
            raise serializers.ValidationError("Senha incorreta.")

        if not user.is_active:
            raise serializers.ValidationError("Conta inativa.")

        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "email": user.email,
                "nome": user.nome,
                "telefone": user.telefone
            }
        }