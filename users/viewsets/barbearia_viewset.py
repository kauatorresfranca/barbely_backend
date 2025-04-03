from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import Barbearia
from users.serializers import BarbeariaSerializer

class BarbeariaViewSet(viewsets.ModelViewSet):
    queryset = Barbearia.objects.all()
    serializer_class = BarbeariaSerializer

    @action(detail=False, methods=['post'])
    def login(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        try:
            barbearia = Barbearia.objects.get(email=email)
            if check_password(password, barbearia.password):
                refresh = RefreshToken.for_user(barbearia)  # Gera o token JWT
                return Response({
                    "message": "Login realizado com sucesso!",
                    "barbearia_id": barbearia.id,
                    "access_token": str(refresh.access_token),  # Retorna o token JWT
                    "refresh_token": str(refresh),  # Token de refresh
                })
            else:
                return Response({"error": "E-mail ou senha inválidos."}, status=status.HTTP_401_UNAUTHORIZED)
        except Barbearia.DoesNotExist:
            return Response({"error": "E-mail ou senha inválidos."}, status=status.HTTP_401_UNAUTHORIZED)
