from django.db import models

class Servico(models.Model):
    barbearia = models.ForeignKey('Barbearia', on_delete=models.CASCADE, related_name='servicos')
    nome = models.CharField(max_length=100)
    duracao_minutos = models.PositiveIntegerField()
    preco = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.nome} ({self.duracao_minutos}min)"
