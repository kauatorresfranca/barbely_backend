from rest_framework import viewsets, permissions
from rest_framework.exceptions import ValidationError
from users.authentication import BarbeariaJWTAuthentication, ClienteJWTAuthentication
from users.models import Cliente
from users.models.barbearia.barbearia_user import BarbeariaUser
from users.models.cliente.cliente_user import ClienteUser
from users.serializers import ClienteSerializer

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

class ClienteViewSet(viewsets.ModelViewSet):
    serializer_class = ClienteSerializer
    authentication_classes = [ClienteJWTAuthentication, BarbeariaJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Verificar se o usuário é um ClienteUser
        if isinstance(user, ClienteUser):
            # Retornar apenas o Cliente associado ao ClienteUser
            return Cliente.objects.filter(user=user)
        # Verificar se o usuário é um BarbeariaUser
        elif isinstance(user, BarbeariaUser):
            # Retornar os clientes associados à barbearia do BarbeariaUser
            return Cliente.objects.filter(barbearia=user.barbearia)
        else:
            # Caso o usuário não seja nem ClienteUser nem BarbeariaUser
            return Cliente.objects.none()

    def get_permissions(self):
        # Permitir criação (POST) sem autenticação
        if self.action == 'create':
            return [permissions.AllowAny()]
        return super().get_permissions()

    def perform_create(self, serializer):
        barbearia_id = self.request.data.get('barbearia')
        if not barbearia_id:
            raise ValidationError({"barbearia": "Este campo é obrigatório."})
        serializer.save()