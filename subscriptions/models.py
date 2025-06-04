from django.db import models
from users.models import Barbearia

class Subscription(models.Model):
    barbearia = models.ForeignKey(Barbearia, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    plan_name = models.CharField(max_length=50)
    billing_cycle = models.CharField(max_length=10, choices=[('monthly', 'Mensal'), ('yearly', 'Anual')])
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pendente'),
        ('active', 'Ativa'),
        ('canceled', 'Cancelada'),
        ('trial', 'Trial'),
        ('expired', 'Expirada'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    trial_end = models.DateTimeField(null=True, blank=True)  # Data de expiração do trial

    def __str__(self):
        return f"{self.plan_name} ({self.billing_cycle}) - {self.barbearia}"

    def is_active(self):
        """Verifica se a assinatura está ativa (incluindo trial)."""
        return self.status in ['active', 'trial'] and (not self.trial_end or self.trial_end > timezone.now())

# Certifique-se de importar timezone se ainda não o fez
from django.utils import timezone