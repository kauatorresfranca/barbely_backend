from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging
from users.authentication import BarbeariaJWTAuthentication
from users.models import Cliente, BarbeariaUser
from users.serializers import ClienteSerializer

logger = logging.getLogger(__name__)

class ClientesDaBarbeariaView(APIView):
    authentication_classes = [BarbeariaJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, barbearia_id):
        logger.debug(f"ClientesDaBarbeariaView chamado para GET /api/clientes/barbearia/{barbearia_id}/")
        clientes = Cliente.objects.filter(barbearia__id=barbearia_id)
        serializer = ClienteSerializer(clientes, many=True)
        return Response(serializer.data)

class ClienteDetailView(APIView):
    authentication_classes = [BarbeariaJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, cliente_id):
        logger.debug(f"ClienteDetailView.get chamado para GET /api/barbearia/clientes/{cliente_id}/")
        try:
            barbearia_id = request.user.id
            cliente = Cliente.objects.get(id=cliente_id, barbearia__id=barbearia_id)
            serializer = ClienteSerializer(cliente)
            return Response(serializer.data)
        except Cliente.DoesNotExist:
            return Response(
                {"detail": "Cliente não encontrado ou não pertence à sua barbearia."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Erro ao buscar cliente {cliente_id}: {str(e)}")
            return Response({"detail": f"Erro interno: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, cliente_id):
        logger.debug(f"ClienteDetailView.delete chamado para DELETE /api/barbearia/clientes/{cliente_id}/")
        try:
            barbearia_id = request.user.id
            cliente = Cliente.objects.get(id=cliente_id, barbearia__id=barbearia_id)
            cliente.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Cliente.DoesNotExist:
            return Response(
                {"detail": "Cliente não encontrado ou não pertence à sua barbearia."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Erro ao deletar cliente {cliente_id}: {str(e)}")
            return Response({"detail": f"Erro interno: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, cliente_id):
        logger.debug(f"ClienteDetailView.put chamado para PUT /api/barbearia/clientes/{cliente_id}/")
        try:
            barbearia_id = request.user.id
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
            logger.error(f"Erro ao atualizar cliente {cliente_id}: {str(e)}")
            return Response({"detail": f"Erro interno: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)