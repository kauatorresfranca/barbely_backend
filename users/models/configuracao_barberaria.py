from django.db import models

class ConfiguracaoBarbearia(models.Model):
    barbearia = models.OneToOneField('Barbearia', on_delete=models.CASCADE, related_name='configuracao')
    intervalo_padrao = models.PositiveIntegerField(default=30)  # em minutos
    prazo_cancelamento_minutos = models.PositiveIntegerField(default=60)  # quanto tempo antes pode cancelar

    def __str__(self):
        return f"Configuração de {self.barbearia.nome}"
