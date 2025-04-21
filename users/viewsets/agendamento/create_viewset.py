from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models.cliente.cliente_user import ClienteUser
from users.models import Agendamento, Cliente, Servico
from users.serializers import AgendamentoSerializer
import logging

logger = logging.getLogger(__name__)

class CriarAgendamentoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logger.debug(f"Usuário autenticado: {request.user}, Autenticado: {request.user.is_authenticated}")

        # Verificar autenticação
        if not request.user.is_authenticated:
            logger.error("Usuário não autenticado.")
            return Response(
                {"detail": "Autenticação necessária. Token inválido ou expirado."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Obter ClienteUser (request.user já é ClienteUser)
        cliente_user = request.user
        if not isinstance(cliente_user, ClienteUser):
            logger.error(f"Usuário {request.user} não é um ClienteUser. Tipo: {type(request.user)}")
            return Response(
                {"detail": "Usuário não é um cliente registrado."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Buscar Cliente
        servico_id = request.data.get('servico')
        try:
            servico = Servico.objects.get(id=servico_id)
            logger.debug(f"Serviço encontrado: {servico}")
        except Servico.DoesNotExist:
            logger.error(f"Serviço não encontrado: {servico_id}")
            return Response(
                {"detail": "Serviço não encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            cliente = Cliente.objects.get(user=cliente_user, barbearia=servico.barbearia)
            logger.debug(f"Cliente encontrado: {cliente}, Nome: {cliente.user.nome}")
        except Cliente.DoesNotExist:
            logger.error(f"Cliente não registrado para barbearia: {servico.barbearia}")
            return Response(
                {"detail": "Cliente não registrado para esta barbearia."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Adicionar o ID do cliente ao payload
        data = request.data.copy()  # Criar uma cópia mutável dos dados
        data['cliente'] = cliente.id

        # Validar e salvar o agendamento usando o serializer
        serializer = AgendamentoSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Agendamento criado: {serializer.data['id']}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Erros de validação: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)