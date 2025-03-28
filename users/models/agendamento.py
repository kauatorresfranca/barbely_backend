from django.db import models
from .barbearia import Barbearia
from .cliente import Cliente

class Agendamento(models.Model):
    barbearia = models.ForeignKey(Barbearia, on_delete=models.CASCADE, related_name="agendamentos")
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="agendamentos")
    data = models.DateField()
    hora = models.TimeField()
    status = models.CharField(
        max_length=10,
        choices=[("pendente", "Pendente"), ("confirmado", "Confirmado"), ("cancelado", "Cancelado")],
        default="pendente"
    )

    def __str__(self):
        return f"{self.cliente.nome} - {self.data} {self.hora}"