from rest_framework import viewsets, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response

from users.authentication import BarbeariaJWTAuthentication
from users.models.endereco_barbearia import EnderecoBarbearia
from users.models.barbearia import Barbearia
from users.serializers.endereco_barbearia_serializer import EnderecoBarbeariaSerializer


class EnderecoBarbeariaViewSet(viewsets.ModelViewSet):
    serializer_class = EnderecoBarbeariaSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [BarbeariaJWTAuthentication]

    def get_queryset(self):
        return EnderecoBarbearia.objects.filter(barbearia=self.request.user)

    def perform_create(self, serializer):
        barbearia = self.request.user
        endereco_existente = EnderecoBarbearia.objects.filter(barbearia=barbearia).first()
        if endereco_existente:
            serializer.update(endereco_existente, serializer.validated_data)
        else:
            serializer.save(barbearia=barbearia)


# View pública baseada em slug
class EnderecoBarbeariaPublicView(APIView):
    def get(self, request, slug):
        try:
            barbearia = Barbearia.objects.get(slug=slug)
            endereco = EnderecoBarbearia.objects.get(barbearia=barbearia)
            serializer = EnderecoBarbeariaSerializer(endereco)
            return Response(serializer.data)
        except Barbearia.DoesNotExist:
            return Response({"detail": "Barbearia não encontrada."}, status=status.HTTP_404_NOT_FOUND)
        except EnderecoBarbearia.DoesNotExist:
            return Response({"detail": "Endereço não cadastrado."}, status=status.HTTP_404_NOT_FOUND)
