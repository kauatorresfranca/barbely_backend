from rest_framework import viewsets, status
from rest_framework.response import Response
from users.models import Barbearia
from users.serializers import BarbeariaSerializer
from rest_framework.permissions import IsAuthenticated
from users.authentication import BarbeariaJWTAuthentication
import logging

logger = logging.getLogger(__name__)

class BarbeariaPerfilViewSet(viewsets.ModelViewSet):
    queryset = Barbearia.objects.all()
    serializer_class = BarbeariaSerializer
    authentication_classes = [BarbeariaJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Obtém a barbearia autenticada a partir do token
        user = self.request.user
        if not isinstance(user, Barbearia):
            raise PermissionError("Usuário não é uma barbearia.")
        return user

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        barbearia = self.get_object()
        logger.info(f"Dados recebidos para atualização (request.data): {request.data}")

        # Atualiza os campos de pagamento diretamente
        if 'pix' in request.data:
            barbearia.pix = request.data['pix'] == 'true' or request.data['pix'] is True
        if 'credit_card' in request.data:
            barbearia.credit_card = request.data['credit_card'] == 'true' or request.data['credit_card'] is True
        if 'debit_card' in request.data:
            barbearia.debit_card = request.data['debit_card'] == 'true' or request.data['debit_card'] is True
        if 'cash' in request.data:
            barbearia.cash = request.data['cash'] == 'true' or request.data['cash'] is True

        serializer = self.get_serializer(barbearia, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Valores salvos: pix={barbearia.pix}, credit_card={barbearia.credit_card}, debit_card={barbearia.debit_card}, cash={barbearia.cash}")
            return Response(serializer.data)
        logger.error(f"Erros de validação: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)