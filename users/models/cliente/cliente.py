from django.db import models
from users.models.barbearia.barbearia import Barbearia
from users.models.cliente.cliente_user import ClienteUser

class Cliente(models.Model):
    barbearia = models.ForeignKey(Barbearia, on_delete=models.CASCADE, related_name="clientes")
    user = models.OneToOneField(ClienteUser, on_delete=models.CASCADE)
    imagem = models.ImageField(upload_to='clientes/', null=True, blank=True)

    def __str__(self):
        try:
            nome = self.user.nome if self.user and self.user.nome else "Cliente sem nome"
            barbearia_nome = self.barbearia.nome_barbearia if self.barbearia else "Barbearia não especificada"
            return f"{nome} ({barbearia_nome})"
        except Exception as e:
            return f"Cliente (Erro: {str(e)})"