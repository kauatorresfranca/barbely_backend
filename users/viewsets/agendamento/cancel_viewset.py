# users/viewsets/agendamento_cancel_view.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from users.models import Agendamento

class CancelarAgendamentoView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            agendamento = Agendamento.objects.get(pk=pk, cliente=request.user)
        except Agendamento.DoesNotExist:
            return Response({"erro": "Agendamento não encontrado ou não pertence a você."}, status=404)

        agendamento.cancelado = True
        agendamento.save()
        return Response({"mensagem": "Agendamento cancelado com sucesso."}, status=200)
