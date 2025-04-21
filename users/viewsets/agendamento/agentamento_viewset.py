from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.models import Agendamento, Funcionario
from users.serializers import AgendamentoSerializer
from users.authentication import BarbeariaJWTAuthentication
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AgendamentoViewSet(viewsets.ModelViewSet):
    queryset = Agendamento.objects.all()
    serializer_class = AgendamentoSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [BarbeariaJWTAuthentication]

    def get_queryset(self):
        barbearia = self.request.user
        if not barbearia:
            logger.error("Nenhuma barbearia autenticada encontrada.")
            return Agendamento.objects.none()
        
        logger.debug(f"Filtrando agendamentos para barbearia: {barbearia}")
        funcionarios = Funcionario.objects.filter(barbearia=barbearia)
        return Agendamento.objects.filter(funcionario__in=funcionarios)

    def get_object(self):
        obj = super().get_object()
        barbearia = self.request.user
        if not barbearia:
            logger.error("Nenhuma barbearia autenticada encontrada ao buscar agendamento.")
            return Response({"error": "Nenhuma barbearia autenticada encontrada."}, status=401)
        
        funcionarios = Funcionario.objects.filter(barbearia=barbearia)
        if obj.funcionario not in funcionarios:
            logger.error(f"Barbearia {barbearia} tentou acessar agendamento de outra barbearia.")
            return Response({"error": "Você não tem permissão para acessar este agendamento."}, status=403)
        return obj

    def list(self, request, *args, **kwargs):
        barbearia = request.user
        if not barbearia:
            logger.error("Nenhuma barbearia autenticada encontrada.")
            return Response({"erro": "Nenhuma barbearia autenticada encontrada."}, status=401)

        logger.debug(f"Buscando agendamentos para barbearia: {barbearia}")

        # Busca todos os funcionários da barbearia
        funcionarios = Funcionario.objects.filter(barbearia=barbearia)
        logger.debug(f"Funcionários encontrados: {funcionarios.count()}")

        if not funcionarios.exists():
            logger.debug("Nenhum funcionário encontrado para a barbearia.")
            return Response([], status=200)

        # Filtrar agendamentos pelos funcionários da barbearia
        agendamentos = self.get_queryset()

        # Filtro opcional por data
        data = request.GET.get('data')
        if data:
            try:
                data_obj = datetime.strptime(data, "%Y-%m-%d").date()
                agendamentos = agendamentos.filter(data=data_obj)
                logger.debug(f"Filtrando por data {data}: {agendamentos.count()} agendamentos")
            except ValueError as e:
                logger.error(f"Formato de data inválido: {data}. Erro: {str(e)}")
                return Response({"erro": "Formato de data inválido. Use YYYY-MM-DD."}, status=400)

        # Filtro opcional por ID do funcionário
        funcionario_id = request.GET.get('funcionario')
        if funcionario_id:
            try:
                # Verificar se o funcionário pertence à barbearia
                Funcionario.objects.get(id=funcionario_id, barbearia=barbearia)
                agendamentos = agendamentos.filter(funcionario_id=funcionario_id)
                logger.debug(f"Filtrando por funcionário {funcionario_id}: {agendamentos.count()} agendamentos")
            except Funcionario.DoesNotExist:
                logger.error(f"Funcionário {funcionario_id} não encontrado ou não pertence à barbearia {barbearia}.")
                return Response({"erro": "Funcionário não encontrado ou não pertence à sua barbearia."}, status=404)
            except ValueError as e:
                logger.error(f"ID de funcionário inválido: {funcionario_id}. Erro: {str(e)}")
                return Response({"erro": "ID de funcionário inválido."}, status=400)

        # Se não houver agendamentos, retornar uma lista vazia com status 200
        if not agendamentos.exists():
            logger.debug("Nenhum agendamento encontrado para os filtros aplicados.")
            return Response([], status=200)

        try:
            serializer = self.get_serializer(agendamentos, many=True)
            logger.debug(f"Serialização concluída: {len(serializer.data)} agendamentos")
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Erro ao serializar agendamentos: {str(e)}")
            return Response({"erro": f"Erro ao buscar agendamentos: {str(e)}"}, status=500)

    def partial_update(self, request, *args, **kwargs):
        barbearia = request.user
        if not barbearia:
            logger.error("Nenhuma barbearia autenticada encontrada ao tentar atualizar agendamento.")
            return Response({"error": "Nenhuma barbearia autenticada encontrada."}, status=401)

        instance = self.get_object()
        if isinstance(instance, Response):
            return instance  # Retorna o erro de permissão, se houver

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.debug(f"Agendamento {instance.id} atualizado: {serializer.data}")
        return Response(serializer.data)