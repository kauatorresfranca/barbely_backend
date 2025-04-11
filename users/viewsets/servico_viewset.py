from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from users.models import Servico
from users.serializers.servico_serializer import ServicoSerializer
from users.authentication import BarbeariaJWTAuthentication

class ServicoViewSet(viewsets.ModelViewSet):
    serializer_class = ServicoSerializer
    queryset = Servico.objects.all()
    authentication_classes = [BarbeariaJWTAuthentication]

    def get_permissions(self):
        if self.request.method in ['GET']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        barbearia_slug = self.request.query_params.get('barbearia_slug')

        # Requisições autenticadas: filtra pelo usuário logado
        if user and user.is_authenticated:
            return Servico.objects.filter(barbearia=user)

        # Requisições públicas com slug: filtra pela barbearia informada
        if barbearia_slug:
            return Servico.objects.filter(barbearia__slug=barbearia_slug)

        # Nenhuma condição válida: retorna queryset vazio
        return Servico.objects.none()

    def perform_create(self, serializer):
        serializer.save(barbearia=self.request.user)
