from django.db import models

class Funcionario(models.Model):
    barbearia = models.ForeignKey('Barbearia', on_delete=models.CASCADE, related_name='funcionarios')
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome
