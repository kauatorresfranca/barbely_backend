from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from users.models import Barbearia
from users.serializers import BarbeariaSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


class BarbeariaViewSet(viewsets.ModelViewSet):
    queryset = Barbearia.objects.all()
    serializer_class = BarbeariaSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        # Permite acesso sem autenticação apenas para login e busca por slug
        if self.action in ['login', 'buscar_por_slug', 'create', 'list']:
            return []
        return super().get_permissions()

    @action(detail=False, methods=['post'])
    def login(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        try:
            barbearia = Barbearia.objects.get(email=email)
            if barbearia.check_password(password):
                refresh = RefreshToken.for_user(barbearia)
                serializer = BarbeariaSerializer(barbearia)
                return Response({
                    "message": "Login realizado com sucesso!",
                    "barbearia_id": barbearia.id,
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                })
            else:
                return Response({"error": "E-mail ou senha inválidos."}, status=status.HTTP_401_UNAUTHORIZED)
        except Barbearia.DoesNotExist:
            return Response({"error": "E-mail ou senha inválidos."}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['get'], url_path='buscar-por-slug/(?P<slug>.+)')
    def buscar_por_slug(self, request, slug=None):
        barbearia = get_object_or_404(Barbearia, slug=slug)
        serializer = BarbeariaSerializer(barbearia)
        return Response(serializer.data)
