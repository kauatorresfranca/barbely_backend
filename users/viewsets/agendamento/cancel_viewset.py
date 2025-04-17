# users/viewsets/agendamento/cancel_viewset.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from users.models import Agendamento, Cliente
from users.authentication import ClienteJWTAuthentication

class CancelarAgendamentoView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [ClienteJWTAuthentication]

    def patch(self, request, pk):
        try:
            # Busca o Cliente associado ao ClienteUser (request.user)
            cliente = Cliente.objects.get(user=request.user)
        except Cliente.DoesNotExist:
            return Response({"erro": "Cliente não encontrado para este usuário."}, status=404)

        try:
            # Filtra o agendamento usando o Cliente
            agendamento = Agendamento.objects.get(pk=pk, cliente=cliente)
        except Agendamento.DoesNotExist:
            return Response({"erro": "Agendamento não encontrado ou não pertence a você."}, status=404)

        if agendamento.status == 'CANCELADO':
            return Response({"erro": "Agendamento já está cancelado."}, status=400)

        agendamento.status = 'CANCELADO'
        agendamento.save()
        return Response({"mensagem": "Agendamento cancelado com sucesso."}, status=200)