from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.models import Agendamento, Funcionario
from users.serializers import AgendamentoSerializer  # Usa o seu serializer normal
from users.authentication import BarbeariaJWTAuthentication
from datetime import datetime

class AgendamentosDaBarbeariaView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [BarbeariaJWTAuthentication]

    def get(self, request):
        barbearia = request.user

        # Busca todos os funcionários da barbearia
        funcionarios = Funcionario.objects.filter(barbearia=barbearia)

        # Pega todos os agendamentos desses funcionários
        agendamentos = Agendamento.objects.filter(funcionario__in=funcionarios)

        # Filtro opcional por data (GET param ?data=2025-04-07)
        data = request.GET.get('data')
        if data:
            try:
                data_obj = datetime.strptime(data, "%Y-%m-%d").date()
                agendamentos = agendamentos.filter(data=data_obj)
            except ValueError:
                return Response({"erro": "Formato de data inválido. Use YYYY-MM-DD."}, status=400)

        # Filtro opcional por ID do funcionário (GET param ?funcionario=3)
        funcionario_id = request.GET.get('funcionario')
        if funcionario_id:
            agendamentos = agendamentos.filter(funcionario_id=funcionario_id)

        serializer = AgendamentoSerializer(agendamentos, many=True)
        return Response(serializer.data)
