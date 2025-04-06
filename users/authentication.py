from rest_framework_simplejwt.authentication import JWTAuthentication
from users.models.cliente_user import ClienteUser

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