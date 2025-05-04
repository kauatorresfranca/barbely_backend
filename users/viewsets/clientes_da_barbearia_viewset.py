from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.authentication import BarbeariaJWTAuthentication
from users.models import Cliente, BarbeariaUser
from users.serializers import ClienteSerializer

class ClientesDaBarbeariaView(APIView):
    authentication_classes = [BarbeariaJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, barbearia_id):
        clientes = Cliente.objects.filter(barbearia__id=barbearia_id)
        serializer = ClienteSerializer(clientes, many=True)
        return Response(serializer.data)

class ClienteDetailView(APIView):
    authentication_classes = [BarbeariaJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, cliente_id):
        print(f"Usuário autenticado: {request.user}, Tipo: {type(request.user)}")
        try:
            barbearia_id = request.user.id  # Usar o ID do Barbearia diretamente
            print(f"Barbearia ID do usuário: {barbearia_id}")
            cliente = Cliente.objects.get(id=cliente_id, barbearia__id=barbearia_id)
            cliente.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Cliente.DoesNotExist:
            return Response(
                {"detail": "Cliente não encontrado ou não pertence à sua barbearia."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({"detail": f"Erro interno: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, cliente_id):
        print(f"Usuário autenticado: {request.user}, Tipo: {type(request.user)}")
        try:
            barbearia_id = request.user.id  # Usar o ID do Barbearia diretamente
            print(f"Barbearia ID do usuário: {barbearia_id}")
            cliente = Cliente.objects.get(id=cliente_id, barbearia__id=barbearia_id)
            
            serializer = ClienteSerializer(cliente, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Cliente.DoesNotExist:
            return Response(
                {"detail": "Cliente não encontrado ou não pertence à sua barbearia."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({"detail": f"Erro interno: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)