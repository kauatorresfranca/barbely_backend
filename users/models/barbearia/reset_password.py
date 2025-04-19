from django.db import models
from django.utils import timezone
import uuid

# ... outros modelos (Cliente, ClienteUser, ClientPasswordResetToken, Barbearia) ...

class BarbeariaPasswordResetToken(models.Model):
    user = models.ForeignKey('Barbearia', on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(hours=1)  # Expira em 1 hora
        super().save(*args, **kwargs)

    def is_valid(self):
        return timezone.now() <= self.expires_at