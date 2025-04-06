from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken

from users.models import HorarioFuncionamento
from users.serializers.horario_funcionamento_serializer import HorarioFuncionamentoSerializer


class HorarioFuncionamentoViewSet(viewsets.ModelViewSet):
    serializer_class = HorarioFuncionamentoSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Obtém o token do cabeçalho da requisição
        token = request.headers.get('Authorization')

        if not token or not token.startswith('Bearer '):
            raise PermissionDenied("Token da barbearia não encontrado.")

        # Extrai o token de acesso da string Bearer <token>
        token = token.split(' ')[1]

        try:
            # Verifica se o token é válido para a barbearia
            access_token = AccessToken(token)
            barbearia_token = access_token.get('barbearia_token')

            if not barbearia_token:
                raise PermissionDenied("Token inválido para a barbearia.")

            # Aqui você pode validar se o barbearia_token corresponde à barbearia associada à requisição
            # Exemplo: Comparar se o barbearia_token corresponde ao ID da barbearia do usuário autenticado
            user = request.user
            if user.barbearia.id != barbearia_token:
                raise PermissionDenied("Token não corresponde à barbearia do usuário autenticado.")

        except Exception as e:
            raise PermissionDenied(f"Erro ao validar o token: {str(e)}")

        # Continuar com a lógica para criar o horário
        return super().create(request, *args, **kwargs)
