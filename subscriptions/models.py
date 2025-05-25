# subscriptions/models.py
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
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.plan_name} ({self.billing_cycle}) - {self.barbearia}"