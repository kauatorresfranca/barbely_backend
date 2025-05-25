# users/models/cliente/cliente.py
from django.db import models
from users.models.barbearia.barbearia import Barbearia
from users.models.cliente.cliente_user import ClienteUser
from django.utils import timezone
from datetime import timedelta

class Cliente(models.Model):
    STATUS_CHOICES = (
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
    )

    barbearia = models.ForeignKey(Barbearia, on_delete=models.CASCADE, related_name="clientes")
    user = models.OneToOneField(ClienteUser, on_delete=models.CASCADE)
    imagem = models.ImageField(upload_to='clientes/', null=True, blank=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='ativo',
        help_text="Indica se o cliente está ativo ou inativo na barbearia."
    )

    def update_status(self):
        """
        Atualiza o status do cliente com base na atividade recente.
        Regra: Inativo se não houver agendamentos nos últimos 6 meses.
        """
        from users.models.agendamento import Agendamento  # Importação local para evitar circularidade
        six_months_ago = timezone.now() - timedelta(days=180)
        recent_agendamentos = Agendamento.objects.filter(
            cliente=self,
            data__gte=six_months_ago,  # Usando 'data' em vez de 'data_horario'
            status__in=['CONFIRMADO', 'CONCLUIDO']
        ).exists()
        if not recent_agendamentos:
            self.status = 'inativo'
        else:
            self.status = 'ativo'
        self.save()

    def __str__(self):
        try:
            nome = self.user.nome if self.user and self.user.nome else "Cliente sem nome"
            barbearia_nome = self.barbearia.nome_barbearia if self.barbearia else "Barbearia não especificada"
            return f"{nome} ({barbearia_nome})"
        except Exception as e:
            return f"Cliente (Erro: {str(e)})"