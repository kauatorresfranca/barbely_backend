from django.db.models.signals import post_save
from django.dispatch import receiver
from .models.barbearia import Barbearia
from .models.horario_funcionamento import HorarioFuncionamento

@receiver(post_save, sender=Barbearia)
def criar_horarios_padrao(sender, instance, created, **kwargs):
    """Cria os horários padrão assim que uma nova barbearia for cadastrada."""
    if created:  # Se for uma nova barbearia
        dias_padrao = [
            (0, None, None, True),  # Domingo fechado
            (1, "07:00", "18:00", False),
            (2, "07:00", "18:00", False),
            (3, "07:00", "18:00", False),
            (4, "07:00", "18:00", False),
            (5, "07:00", "18:00", False),
            (6, "08:00", "14:00", False),  # Sábado com horário reduzido
        ]
        
        for dia, abertura, fechamento, fechado in dias_padrao:
            HorarioFuncionamento.objects.create(
                barbearia=instance,
                dia_semana=dia,
                horario_abertura=abertura,
                horario_fechamento=fechamento,
                fechado=fechado
            )
