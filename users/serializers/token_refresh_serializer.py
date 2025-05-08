from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import InvalidToken
import jwt
from django.conf import settings

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        refresh_token = attrs.get('refresh')
        if not refresh_token:
            raise InvalidToken("No valid refresh token provided")

        try:
            # Decodificar o token para validar manualmente
            payload = jwt.decode(refresh_token, settings.SIMPLE_JWT['SIGNING_KEY'], algorithms=[settings.SIMPLE_JWT['ALGORITHM']])
            user_id = payload.get(settings.SIMPLE_JWT['USER_ID_CLAIM'])
            user_type = payload.get('user_type')

            if not user_id or not user_type:
                raise InvalidToken("Token inválido: user_id ou user_type não encontrado")

            # Não buscamos o usuário aqui; apenas validamos o token
            # A lógica de busca do usuário será feita no CustomTokenRefreshView
            refresh = self.context['view'].get_token(refresh_token)
            return {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        except jwt.InvalidTokenError:
            raise InvalidToken("Refresh token inválido")