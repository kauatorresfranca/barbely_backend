from django.db import models

class Funcionario(models.Model):
    barbearia = models.ForeignKey('Barbearia', on_delete=models.CASCADE, related_name='funcionarios')
    nome = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True, blank=True)
    telefone = models.CharField(max_length=15, null=True, blank=True)
    imagem = models.ImageField(upload_to='funcionarios/', null=True, blank=True)

    def __str__(self):
        return self.nome