from rest_framework import viewsets
from users.authentication import BarbeariaJWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from users.models import Funcionario
from users.serializers.funcionario_serializer import FuncionarioSerializer

class FuncionarioViewSet(viewsets.ModelViewSet):
    serializer_class = FuncionarioSerializer
    queryset = Funcionario.objects.all()
    authentication_classes = [BarbeariaJWTAuthentication]

    def get_permissions(self):
        if self.request.method in ['GET']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if self.request.method == 'GET' and not user or not user.is_authenticated:
            # Quando for uma listagem pública, pode pegar tudo (ou filtrar depois por barbearia via query params)
            return Funcionario.objects.all()
        return Funcionario.objects.filter(barbearia=user)

    def perform_create(self, serializer):
        serializer.save(barbearia=self.request.user)
