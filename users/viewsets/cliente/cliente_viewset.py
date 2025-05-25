from rest_framework import viewsets, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from users.authentication import BarbeariaJWTAuthentication, ClienteJWTAuthentication
from users.models import Cliente, Agendamento
from users.models.barbearia.barbearia_user import BarbeariaUser
from users.models.cliente.cliente_user import ClienteUser
from users.serializers import ClienteSerializer
from users.serializers.agendamento_serializer import AgendamentoSerializer

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
        if isinstance(user, ClienteUser):
            return Cliente.objects.filter(user=user)
        elif isinstance(user, BarbeariaUser):
            return Cliente.objects.filter(barbearia=user.barbearia)
        else:
            return Cliente.objects.none()

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return super().get_permissions()

    def perform_create(self, serializer):
        barbearia_id = self.request.data.get('barbearia')
        if not barbearia_id:
            raise ValidationError({"barbearia": "Este campo é obrigatório."})
        serializer.save()

class ClienteDetailView(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['patch'], url_path='update-status')
    def update_status(self, request, pk=None):
        cliente = self.get_object()
        new_status = request.data.get('status')
        if new_status not in [choice[0] for choice in Cliente.STATUS_CHOICES]:
            return Response(
                {"detail": "Status inválido. Use 'ativo' ou 'inativo'."},
                status=status.HTTP_400_BAD_REQUEST
            )
        cliente.status = new_status
        cliente.save()
        serializer = self.get_serializer(cliente)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='historico')
    def historico(self, request, pk=None):
        cliente = self.get_object()
        agendamentos = Agendamento.objects.filter(cliente=cliente).order_by('-data', '-hora_inicio')
        serializer = AgendamentoSerializer(agendamentos, many=True)
        return Response(serializer.data)