from django.db import models
from django.utils.text import slugify
from .barbearia import Barbearia

class Cliente(models.Model):
    barbearia = models.ForeignKey(Barbearia, on_delete=models.CASCADE, related_name="clientes")
    nome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True, blank=True, null=True)

    def __str__(self):
        return f"{self.nome} ({self.barbearia.nome})"