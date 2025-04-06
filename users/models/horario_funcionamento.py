from django.db import models
from .barbearia import Barbearia  # Importando o modelo da barbearia

class HorarioFuncionamento(models.Model):
    DIAS_SEMANA = [
        (0, "Domingo"),
        (1, "Segunda-feira"),
        (2, "Terça-feira"),
        (3, "Quarta-feira"),
        (4, "Quinta-feira"),
        (5, "Sexta-feira"),
        (6, "Sábado"),
    ]

    barbearia = models.ForeignKey(Barbearia, on_delete=models.CASCADE, related_name="horarios")
    dia_semana = models.IntegerField(choices=DIAS_SEMANA)
    horario_abertura = models.TimeField(blank=True, null=True)
    horario_fechamento = models.TimeField(blank=True, null=True)
    fechado = models.BooleanField(default=False)

    class Meta:
        unique_together = ("barbearia", "dia_semana")  # Garante que não tenha dias duplicados
        ordering = ["dia_semana"]  # Organiza os horários por dia da semana

    def __str__(self):
        status = "Fechado" if self.fechado else f"{self.horario_abertura} - {self.horario_fechamento}"
        return f"{self.get_dia_semana_display()}: {status}"
