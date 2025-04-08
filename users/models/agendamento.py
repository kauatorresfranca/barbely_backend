from django.db import models
from .funcionario import Funcionario
from .servico import Servico

class Agendamento(models.Model):
    cliente = models.ForeignKey('ClienteUser', on_delete=models.CASCADE, related_name='agendamentos')
    funcionario = models.ForeignKey(Funcionario, on_delete=models.CASCADE, related_name='agendamentos')
    servico = models.ForeignKey(Servico, on_delete=models.CASCADE)
    data = models.DateField()
    hora_inicio = models.TimeField()
    criado_em = models.DateTimeField(auto_now_add=True)
    cancelado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.servico.nome} com {self.funcionario.nome} em {self.data} às {self.hora_inicio}"
