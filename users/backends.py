from django.contrib.auth.backends import BaseBackend
from users.models.cliente.cliente_user import ClienteUser

class ClienteBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = ClienteUser.objects.get(email=email)
            if user.check_password(password):
                return user
        except ClienteUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return ClienteUser.objects.get(pk=user_id)
        except ClienteUser.DoesNotExist:
            return None
