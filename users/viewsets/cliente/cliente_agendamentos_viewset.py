# users/viewsets/agendamento/cliente_agendamentos_viewset.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.authentication import ClienteJWTAuthentication
from users.models import Agendamento
from users.serializers import AgendamentoSerializer
import logging

logger = logging.getLogger(__name__)

class ClienteAgendamentosView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [ClienteJWTAuthentication]

    def get(self, request):
        cliente = request.user.cliente  # Assumes the user has a related `Cliente` model
        logger.debug(f"Buscando agendamentos para cliente: {cliente}")

        # Fetch appointments for the authenticated client
        agendamentos = Agendamento.objects.filter(cliente=cliente)
        logger.debug(f"Agendamentos encontrados: {agendamentos.count()}")

        try:
            serializer = AgendamentoSerializer(agendamentos, many=True)
            logger.debug(f"Serialização concluída: {len(serializer.data)} agendamentos")
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Erro ao serializar agendamentos: {str(e)}")
            return Response({"erro": f"Erro ao buscar agendamentos: {str(e)}"}, status=500)