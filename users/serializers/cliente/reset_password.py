from rest_framework import serializers
from users.models import Cliente, ClientPasswordResetToken

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    slug = serializers.CharField(required=False)  # Opcional, usado para o link de redefinição

    def validate_email(self, value):
        if not Cliente.objects.filter(user__email=value).exists():
            raise serializers.ValidationError("E-mail não encontrado.")
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    new_password = serializers.CharField(write_only=True, min_length=8)