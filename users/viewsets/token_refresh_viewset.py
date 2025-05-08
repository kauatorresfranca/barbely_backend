from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
import jwt
from django.conf import settings
from users.models.barbearia.barbearia import Barbearia
from users.models.cliente.cliente_user import ClienteUser
from users.serializers.token_refresh_serializer import CustomTokenRefreshSerializer
import logging

logger = logging.getLogger(__name__)

class CustomTokenRefreshView(APIView):
    serializer_class = CustomTokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'view': self})

        try:
            serializer.is_valid(raise_exception=True)
            refresh_token = request.data.get('refresh')

            # Decodificar o refresh token para obter o user_type e user_id
            payload = jwt.decode(refresh_token, settings.SIMPLE_JWT['SIGNING_KEY'], algorithms=[settings.SIMPLE_JWT['ALGORITHM']])
            user_id = payload.get(settings.SIMPLE_JWT['USER_ID_CLAIM'])
            user_type = payload.get('user_type')

            if not user_id or not user_type:
                return Response({"error": "Token inválido: user_id ou user_type não encontrado"}, status=status.HTTP_401_UNAUTHORIZED)

            # Validar o usuário com base no user_type
            if user_type == 'barbearia':
                try:
                    user = Barbearia.objects.get(id=user_id)
                except Barbearia.DoesNotExist:
                    return Response({"error": "Barbearia não encontrada"}, status=status.HTTP_401_UNAUTHORIZED)
            elif user_type == 'cliente':
                try:
                    user = ClienteUser.objects.get(id=user_id)
                except ClienteUser.DoesNotExist:
                    return Response({"error": "Cliente não encontrado"}, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({"error": "Tipo de usuário inválido"}, status=status.HTTP_401_UNAUTHORIZED)

            # Gerar novos tokens manualmente
            refresh = RefreshToken.for_user(user)
            refresh.payload['user_type'] = user_type  # Preservar o user_type no novo token
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_200_OK)

        except TokenError as e:
            logger.error(f"Erro ao validar refresh token: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logger.error(f"Erro inesperado ao renovar token: {str(e)}")
            return Response({"error": "Erro interno ao renovar token"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_token(self, refresh_token):
        return RefreshToken(refresh_token)