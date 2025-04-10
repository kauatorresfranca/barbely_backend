from rest_framework import serializers
from users.models.funcionario import Funcionario

class FuncionarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Funcionario
        fields = ['id', 'barbearia', 'nome']
        read_only_fields = ['barbearia']

    def validate_nome(self, value):
        barbearia = self.context['request'].user
        if Funcionario.objects.filter(barbearia=barbearia, nome=value).exists():
            raise serializers.ValidationError("Já existe um funcionário com esse nome.")
        return value
