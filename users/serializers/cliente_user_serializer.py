from rest_framework import serializers
from users.models.cliente_user import ClienteUser
from rest_framework_simplejwt.tokens import RefreshToken

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
