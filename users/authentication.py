from rest_framework_simplejwt.authentication import JWTAuthentication
from users.models.cliente_user import ClienteUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from users.models import Barbearia
from rest_framework.exceptions import AuthenticationFailed

class ClienteJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            user_id = validated_token.get("user_id")
            if user_id is None:
                raise Exception("Token inválido: sem user_id")

            user = ClienteUser.objects.get(id=user_id)

            if not user.is_active:
                raise Exception("Usuário inativo")

            return user

        except ClienteUser.DoesNotExist:
            raise Exception("Usuário não encontrado")  

class BarbeariaJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            user_id = validated_token["user_id"]
            user = Barbearia.objects.get(id=user_id)
        except Barbearia.DoesNotExist:
            raise AuthenticationFailed("Usuário não encontrado", code="user_not_found")
        return user
