from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from users.models import Cliente
from users.serializers import ClienteSerializer

class ClientesDaBarbeariaView(APIView):
    authentication_classes = [JWTAuthentication]  # <- forçando a autenticação padrão (usuário do sistema)
    permission_classes = [IsAuthenticated]

    def get(self, request, barbearia_id):
        clientes = Cliente.objects.filter(barbearia__id=barbearia_id)
        serializer = ClienteSerializer(clientes, many=True)
        return Response(serializer.data)
