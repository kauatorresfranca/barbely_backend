from rest_framework import serializers
from django.contrib.auth.models import Group, Permission
from ..models.barbearia import Barbearia

class BarbeariaSerializer(serializers.ModelSerializer):
    groups = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Group.objects.all(), required=False
    )
    user_permissions = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Permission.objects.all(), required=False
    )

    class Meta:
        model = Barbearia
        fields = ['id', 'nome', 'email', 'username', 'groups', 'user_permissions']
        extra_kwargs = {'username': {'required': False}}

    def create(self, validated_data):
        if 'username' not in validated_data or not validated_data['username']:
            base_username = validated_data['nome'].lower().replace(" ", "_")
            contador = 1
            new_username = base_username

            # Garante que o username seja único no banco
            while Barbearia.objects.filter(username=new_username).exists():
                new_username = f"{base_username}_{contador}"
                contador += 1
            
            validated_data['username'] = new_username  # Define o username gerado

        return super().create(validated_data)
