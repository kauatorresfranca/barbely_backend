from django.db import models
from users.models.barbearia.barbearia import Barbearia

class Custo(models.Model):
    TIPO_CHOICES = (
        ('fixed', 'Fixo'),
        ('variable', 'Variável'),
    )

    barbearia = models.ForeignKey(Barbearia, on_delete=models.CASCADE)
    descricao = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateField()
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='fixed')
    criado_em = models.DateTimeField(auto_now_add=True)