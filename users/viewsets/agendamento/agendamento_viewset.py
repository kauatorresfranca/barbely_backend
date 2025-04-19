from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.models import Agendamento, Funcionario
from users.serializers import AgendamentoSerializer
from users.authentication import BarbeariaJWTAuthentication
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AgendamentosDaBarbeariaView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [BarbeariaJWTAuthentication]

    def get(self, request):
        barbearia = request.user
        logger.debug(f"Buscando agendamentos para barbearia: {barbearia}")

        # Busca todos os funcionários da barbearia
        funcionarios = Funcionario.objects.filter(barbearia=barbearia)
        logger.debug(f"Funcionários encontrados: {funcionarios.count()}")

        # Pega todos os agendamentos desses funcionários
        agendamentos = Agendamento.objects.filter(funcionario__in=funcionarios)
        logger.debug(f"Agendamentos encontrados: {agendamentos.count()}")

        # Filtro opcional por data
        data = request.GET.get('data')
        if data:
            try:
                data_obj = datetime.strptime(data, "%Y-%m-%d").date()
                agendamentos = agendamentos.filter(data=data_obj)
                logger.debug(f"Filtrando por data {data}: {agendamentos.count()} agendamentos")
            except ValueError:
                logger.error(f"Formato de data inválido: {data}")
                return Response({"erro": "Formato de data inválido. Use YYYY-MM-DD."}, status=400)

        # Filtro opcional por ID do funcionário
        funcionario_id = request.GET.get('funcionario')
        if funcionario_id:
            agendamentos = agendamentos.filter(funcionario_id=funcionario_id)
            logger.debug(f"Filtrando por funcionário {funcionario_id}: {agendamentos.count()} agendamentos")

        try:
            serializer = AgendamentoSerializer(agendamentos, many=True)
            logger.debug(f"Serialização concluída: {len(serializer.data)} agendamentos")
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Erro ao serializar agendamentos: {str(e)}")
            return Response({"erro": f"Erro ao buscar agendamentos: {str(e)}"}, status=500)