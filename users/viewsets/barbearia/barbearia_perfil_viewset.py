from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models.barbearia.barbearia import Barbearia
from users.serializers.barbearia.barbearia_perfil_serializer import BarbeariaUpdateSerializer
from users.authentication import BarbeariaJWTAuthentication
from django.utils.text import slugify

class BarbeariaPerfilViewSet(viewsets.ViewSet):
    authentication_classes = [BarbeariaJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def retrieve(self, request):
        barbearia = request.user
        serializer = BarbeariaUpdateSerializer(barbearia)
        return Response(serializer.data)

    def update(self, request):
        barbearia = request.user
        serializer = BarbeariaUpdateSerializer(barbearia, data=request.data, partial=True)
        if serializer.is_valid():
            barbearia = serializer.save()
            
            # Atualiza o slug baseado no nome_barbearia
            if 'nome_barbearia' in request.data:
                novo_slug = slugify(barbearia.nome_barbearia)
                barbearia.slug = novo_slug
            
            # Atualiza o username se vier no request
            if 'username' in request.data:
                barbearia.username = request.data['username']
            
            barbearia.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
