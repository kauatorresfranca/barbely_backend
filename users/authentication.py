from rest_framework_simplejwt.authentication import JWTAuthentication
from users.models.cliente.cliente_user import ClienteUser
from users.models.barbearia.barbearia import Barbearia
from rest_framework.exceptions import AuthenticationFailed
import logging

logger = logging.getLogger(__name__)

class ClienteJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            user_id = validated_token.get("user_id")
            if user_id is None:
                raise AuthenticationFailed("Token inválido: sem user_id", code="invalid_token")

            user_type = validated_token.get("user_type")
            if user_type != "cliente":
                raise AuthenticationFailed("Este endpoint é restrito a usuários do tipo cliente", code="wrong_user_type")

            user = ClienteUser.objects.get(id=user_id)

            if not user.is_active:
                raise AuthenticationFailed("Usuário inativo", code="inactive_user")

            return user

        except ClienteUser.DoesNotExist:
            logger.error(f"Usuário cliente não encontrado para user_id: {user_id}")
            raise AuthenticationFailed("Usuário não encontrado", code="user_not_found")
        except Exception as e:
            logger.error(f"Erro na autenticação do cliente: {str(e)}")
            raise AuthenticationFailed(f"Erro na autenticação: {str(e)}", code="authentication_error")

class BarbeariaJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            user_id = validated_token["user_id"]
            user_type = validated_token.get("user_type")
            if user_type != "barbearia":
                raise AuthenticationFailed("Este endpoint é restrito a usuários do tipo barbearia", code="wrong_user_type")

            user = Barbearia.objects.get(id=user_id)
            return user
        except Barbearia.DoesNotExist:
            raise AuthenticationFailed("Usuário não encontrado", code="user_not_found")
        except Exception as e:
            logger.error(f"Erro na autenticação da barbearia: {str(e)}")
            raise AuthenticationFailed(f"Erro na autenticação: {str(e)}", code="authentication_error")