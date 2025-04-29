from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from users.models.barbearia.barbearia import Barbearia
from users.serializers import CustoSerializer
from users.models.custo import Custo
from django_filters.rest_framework import DjangoFilterBackend
from users.authentication import BarbeariaJWTAuthentication
import logging

logger = logging.getLogger(__name__)

class CustoViewSet(viewsets.ModelViewSet):
    queryset = Custo.objects.all()
    serializer_class = CustoSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [BarbeariaJWTAuthentication]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['data']

    def get_queryset(self):
        # Filtra os custos pela barbearia do usuário logado
        if not isinstance(self.request.user, Barbearia):
            logger.error(f"Usuário não é Barbearia: {self.request.user}")
            return Custo.objects.none()
        logger.debug(f"Filtrando custos para barbearia: {self.request.user}")
        queryset = Custo.objects.filter(barbearia=self.request.user)
        logger.debug(f"Custos encontrados: {queryset.count()}")
        return queryset

    def perform_create(self, serializer):
        logger.debug(f"Criando custo para barbearia: {self.request.user}")
        serializer.save(barbearia=self.request.user)