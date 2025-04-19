from rest_framework import serializers
from users.models import Cliente, ClientPasswordResetToken, Barbearia, BarbeariaPasswordResetToken

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    slug = serializers.CharField(required=False)

    def validate_email(self, value):
        if not Cliente.objects.filter(user__email=value).exists():
            raise serializers.ValidationError("E-mail não encontrado.")
        return value

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    new_password = serializers.CharField(write_only=True, min_length=8)

class BarbeariaPasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not Barbearia.objects.filter(email=value).exists():
            raise serializers.ValidationError("E-mail não encontrado.")
        return value

class BarbeariaPasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    new_password = serializers.CharField(write_only=True, min_length=8)