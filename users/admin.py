from django.contrib import admin
from users.models import Funcionario, Servico, Barbearia, Agendamento, HorarioFuncionamento

admin.site.register(Funcionario)
admin.site.register(Servico)
admin.site.register(Barbearia)
admin.site.register(Agendamento)
admin.site.register(HorarioFuncionamento)
