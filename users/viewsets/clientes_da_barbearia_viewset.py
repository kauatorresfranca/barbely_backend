from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.authentication import BarbeariaJWTAuthentication
from users.models import Cliente
from users.serializers import ClienteSerializer

class ClientesDaBarbeariaView(APIView):
    authentication_classes = [BarbeariaJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, barbearia_id):
        clientes = Cliente.objects.filter(barbearia__id=barbearia_id)
        serializer = ClienteSerializer(clientes, many=True)
        return Response(serializer.data)

# Nova view para gerenciar clientes individuais (ex.: DELETE)
class ClienteDetailView(APIView):
    authentication_classes = [BarbeariaJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, cliente_id):
        try:
            cliente = Cliente.objects.get(id=cliente_id, barbearia__id=request.user.barbearia.id)
            cliente.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Cliente.DoesNotExist:
            return Response(
                {"detail": "Cliente não encontrado ou não pertence à sua barbearia."},
                status=status.HTTP_404_NOT_FOUND
            )