from rest_framework import serializers
from users.models.funcionario import Funcionario
import logging

logger = logging.getLogger(__name__)

class FuncionarioSerializer(serializers.ModelSerializer):
    fotoPerfil = serializers.SerializerMethodField()

    class Meta:
        model = Funcionario
        fields = ['id', 'barbearia', 'nome', 'email', 'telefone', 'imagem', 'fotoPerfil']
        read_only_fields = ['barbearia']
        extra_kwargs = {
            'imagem': {'required': False},
            'email': {'required': False},
            'telefone': {'required': False},
        }

    def get_fotoPerfil(self, obj):
        if obj.imagem and hasattr(obj.imagem, 'url'):
            return obj.imagem.url
        return None

    def validate_nome(self, value):
        barbearia = self.context['request'].user
        if self.instance:
            # Allow updating the same name for the same employee
            if Funcionario.objects.filter(barbearia=barbearia, nome=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Já existe um funcionário com esse nome.")
        else:
            if Funcionario.objects.filter(barbearia=barbearia, nome=value).exists():
                raise serializers.ValidationError("Já existe um funcionário com esse nome.")
        return value

    def validate_email(self, value):
        if value:
            barbearia = self.context['request'].user
            if self.instance:
                # Allow updating the same email for the same employee
                if Funcionario.objects.filter(barbearia=barbearia, email=value).exclude(id=self.instance.id).exists():
                    raise serializers.ValidationError("Já existe um funcionário com esse email.")
            else:
                if Funcionario.objects.filter(barbearia=barbearia, email=value).exists():
                    raise serializers.ValidationError("Já existe um funcionário com esse email.")
        return value

    def validate_telefone(self, value):
        if value:
            # Basic phone number validation (adjust as needed)
            if not value.replace(' ', '').replace('-', '').replace('(', '').replace(')', '').isdigit():
                raise serializers.ValidationError("O telefone deve conter apenas números, espaços, parênteses ou hífens.")
            if len(value) < 10 or len(value) > 15:
                raise serializers.ValidationError("O telefone deve ter entre 10 e 15 caracteres.")
        return value

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