# users/viewsets/agendamento/atualizar_status_viewset.py
from django.utils import timezone
from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from users.models import Agendamento

class AtualizarStatusAgendamentosView(APIView):
    permission_classes = [IsAdminUser]  # Apenas admin pode executar

    def post(self, request):
        agora = timezone.now()
        agendamentos = Agendamento.objects.filter(status='CONFIRMADO')

        for agendamento in agendamentos:
            # Combina data e hora_inicio para comparar com o momento atual
            data_hora_agendamento = datetime.combine(agendamento.data, agendamento.hora_inicio)
            data_hora_agendamento = timezone.make_aware(data_hora_agendamento)

            if data_hora_agendamento < agora:
                agendamento.status = 'EXPIRADO'  # Ou 'CONCLUIDO', dependendo da lógica
                agendamento.save()

        return Response({"mensagem": "Status dos agendamentos atualizados."}, status=200)