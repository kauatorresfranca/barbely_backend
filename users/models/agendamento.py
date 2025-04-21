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
    preco_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Novo campo
    criado_em = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.preco_total and self.servico:
            self.preco_total = self.servico.preco  # Preenche com o preço do serviço
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.servico.nome} - {self.data} {self.hora_inicio}"