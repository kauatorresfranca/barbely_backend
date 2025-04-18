from django.db import models
from users.models.barbearia import Barbearia
from users.models.cliente_user import ClienteUser

class Cliente(models.Model):
    barbearia = models.ForeignKey(Barbearia, on_delete=models.CASCADE, related_name="clientes")
    user = models.OneToOneField(ClienteUser, on_delete=models.CASCADE)
    imagem = models.ImageField(upload_to='clientes/', null=True, blank=True)

    def __str__(self):
        return f"{self.nome} ({self.barbearia.nome_barbearia})"
