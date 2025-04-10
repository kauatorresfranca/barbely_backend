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
        if self.request.method == 'GET' and (not user or not user.is_authenticated):
            # Listagem pública - pode adaptar para filtrar por barbearia via query param no futuro
            return Servico.objects.all()
        return Servico.objects.filter(barbearia=user)

    def perform_create(self, serializer):
        serializer.save(barbearia=self.request.user)
