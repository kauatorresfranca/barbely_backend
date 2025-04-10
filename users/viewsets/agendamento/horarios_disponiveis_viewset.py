from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from datetime import datetime
from users.models import Funcionario, Servico
from users.utils.calcular_horarios_disponiveis import calcular_horarios_disponiveis


class HorariosDisponiveisView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        funcionario_id = request.GET.get('funcionario')
        data_str = request.GET.get('data')
        servico_id = request.GET.get('servico')

        if not funcionario_id or not data_str or not servico_id:
            return Response(
                {'erro': 'Parâmetros "funcionario", "data" e "servico" são obrigatórios.'},
                status=400
            )

        try:
            data = datetime.strptime(data_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'erro': 'Data inválida. Use o formato YYYY-MM-DD.'}, status=400)

        try:
            funcionario = Funcionario.objects.get(id=int(funcionario_id))
        except (Funcionario.DoesNotExist, ValueError):
            return Response({'erro': 'Funcionário não encontrado.'}, status=404)

        try:
            servico = Servico.objects.get(id=int(servico_id), barbearia=funcionario.barbearia)
        except (Servico.DoesNotExist, ValueError):
            return Response({'erro': 'Serviço não encontrado ou não pertence à barbearia do funcionário.'}, status=404)

        horarios = calcular_horarios_disponiveis(
            funcionario.barbearia, funcionario, data, servico.duracao_minutos
        )

        return Response({'horarios_disponiveis': horarios})
