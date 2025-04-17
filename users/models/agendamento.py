# users/models/agendamento.py
from django.db import models
from .funcionario import Funcionario
from .servico import Servico

class Agendamento(models.Model):
    STATUS_CHOICES = (
        ('CONFIRMADO', 'Confirmado'),
        ('CANCELADO', 'Cancelado'),
        ('EXPIRADO', 'Expirado'),
        ('CONCLUIDO', 'Concluído'),
    )

    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE)
    funcionario = models.ForeignKey('Funcionario', on_delete=models.CASCADE)
    servico = models.ForeignKey('Servico', on_delete=models.CASCADE)
    data = models.DateField()
    hora_inicio = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='CONFIRMADO')
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.servico.nome} - {self.data} {self.hora_inicio}"