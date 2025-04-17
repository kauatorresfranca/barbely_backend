from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models.cliente_user import ClienteUser
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

        # Validar dados do request
        serializer = AgendamentoSerializer(data=request.data)
        if not serializer.is_valid():
            logger.debug(f"Erros de validação: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Obter serviço
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

        # Buscar Cliente
        try:
            cliente = Cliente.objects.get(user=cliente_user, barbearia=servico.barbearia)
            logger.debug(f"Cliente encontrado: {cliente}")
        except Cliente.DoesNotExist:
            logger.error(f"Cliente não registrado para barbearia: {servico.barbearia}")
            return Response(
                {"detail": "Cliente não registrado para esta barbearia."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Criar agendamento manualmente para evitar problemas com o serializer
        try:
            agendamento_data = serializer.validated_data
            agendamento = Agendamento(
                cliente=cliente,
                funcionario=agendamento_data['funcionario'],
                servico=agendamento_data['servico'],
                data=agendamento_data['data'],
                hora_inicio=agendamento_data['hora_inicio'],
                status='CONFIRMADO'
            )
            agendamento.save()
            logger.info(f"Agendamento criado: {agendamento.id}")
            return Response(
                AgendamentoSerializer(agendamento).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"Erro ao salvar agendamento: {str(e)}")
            return Response(
                {"detail": f"Erro ao criar agendamento: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )