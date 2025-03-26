from django.db import models
from django.contrib.auth.models import AbstractUser

class Barbearia(AbstractUser):
    nome = models.CharField(max_length=100, default="Desconhecido")
    username = models.CharField(max_length=150, unique=True, blank=False, null=False, default="temp_username")

    class Meta:
        app_label = 'users'
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='barbearia_set',
        blank=True,
        help_text='The groups this user belongs to.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='barbearia_permissions_set',
        blank=True,
        help_text='Specific permissions for this user.'
    )
