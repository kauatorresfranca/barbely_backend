from django.db import models

class EnderecoBarbearia(models.Model):
    cep = models.CharField(max_length=9)
    estado = models.CharField(max_length=50)
    cidade = models.CharField(max_length=100)
    bairro = models.CharField(max_length=100)
    endereco = models.CharField(max_length=255)
    numero = models.CharField(max_length=20)
    complemento = models.CharField(max_length=255, blank=True, null=True)

    # Se você quiser vincular o endereço diretamente à barbearia:
    barbearia = models.OneToOneField(
        "users.Barbearia", 
        on_delete=models.CASCADE,
        related_name="endereco"
    )

    def __str__(self):
        return f"{self.endereco}, {self.numero} - {self.cidade}/{self.estado}"
