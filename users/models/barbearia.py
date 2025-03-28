from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import AbstractUser, Group, Permission

# 📌 Modelo da Barbearia
class Barbearia(AbstractUser):
    nome = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True, null=True)
    cnpj = models.CharField(max_length=14, unique=True, blank=True, null=True)  # Agora pode ser opcional
    plano = models.CharField(
        max_length=20, 
        choices=[("free", "Grátis"), ("premium", "Premium")]
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    groups = models.ManyToManyField(Group, related_name="barbearia_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="barbearia_permissions", blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)  # Gerar slug automaticamente
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome
