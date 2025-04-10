from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.viewsets.agendamento.agendamento_viewset import AgendamentosDaBarbeariaView
from users.viewsets.barbearia.barbearia_user_viewset import BarbeariaUserInfoView
from users.viewsets.agendamento.create_viewset import CriarAgendamentoView
from users.viewsets.agendamento.cancel_viewset import CancelarAgendamentoView
from users.viewsets.agendamento.horarios_disponiveis_viewset import HorariosDisponiveisView

from .viewsets.barbearia.barbearia_viewset import BarbeariaViewSet
from .viewsets.horario_funcionamento_viewset import HorarioFuncionamentoViewSet
from .viewsets.cliente.cliente_viewset import ClienteViewSet
from .viewsets.cliente.cliente_user_viewset import ClienteLoginView, ClienteUserInfoView
from .viewsets.clientes_da_barbearia_viewset import ClientesDaBarbeariaView

# 👇 IMPORTANDO OS NOVOS VIEWSETS
from .viewsets.funcionario_viewset import FuncionarioViewSet
from .viewsets.servico_viewset import ServicoViewSet

from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'barbearias', BarbeariaViewSet, basename='barbearia')
router.register(r'horarios', HorarioFuncionamentoViewSet, basename='horariofuncionamento')
router.register(r'clientes', ClienteViewSet, basename='clientes')
# 👇 REGISTRANDO OS NOVOS VIEWSETS
router.register(r'funcionarios', FuncionarioViewSet, basename='funcionario')
router.register(r'servicos', ServicoViewSet, basename='servico')

urlpatterns = [
    path('clientes/login/', ClienteLoginView.as_view(), name='cliente-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='cliente-token-refresh'),
    path('barbearia/agendamentos/', AgendamentosDaBarbeariaView.as_view(), name='agendamentos-da-barbearia'),
    path('barbearias/user-info/', BarbeariaUserInfoView.as_view(), name='barbearia-user-info'),
    path('clientes/user-info/', ClienteUserInfoView.as_view(), name='cliente-user-info'),
    path('clientes/barbearia/<int:barbearia_id>/', ClientesDaBarbeariaView.as_view(), name='clientes-da-barbearia'),
    path('agendamentos/criar/', CriarAgendamentoView.as_view(), name='criar-agendamento'),
    path('agendamentos/<int:pk>/cancelar/', CancelarAgendamentoView.as_view(), name='cancelar-agendamento'),
    path('agendamentos/horarios-disponiveis/', HorariosDisponiveisView.as_view(), name='horarios_disponiveis'),
    path('', include(router.urls))
]
