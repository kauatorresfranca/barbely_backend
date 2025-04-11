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
        barbearia_slug = self.request.query_params.get('barbearia_slug')

        if user and user.is_authenticated:
            return Funcionario.objects.filter(barbearia=user)

        if barbearia_slug:
            return Funcionario.objects.filter(barbearia__slug=barbearia_slug)

        return Funcionario.objects.none()  # evita listar tudo quando não tem filtro

    def perform_create(self, serializer):
        serializer.save(barbearia=self.request.user)
