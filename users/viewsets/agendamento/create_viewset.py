from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models.cliente_user import ClienteUser
from users.models import Agendamento
from users.serializers import AgendamentoSerializer

class CriarAgendamentoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        if not isinstance(user, ClienteUser):
            return Response({"detail": "Apenas clientes podem criar agendamentos."}, status=status.HTTP_403_FORBIDDEN)

        serializer = AgendamentoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(cliente=user)  # ou .save(cliente=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
