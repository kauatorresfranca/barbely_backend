from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets.barbearia.custo_viewset import CustoViewSet
from .viewsets.agendamento.agendamento_da_barbearia_viewset import AgendamentosDaBarbeariaView
from .viewsets.barbearia.barbearia_perfil_viewset import BarbeariaPerfilViewSet
from .viewsets.agendamento.create_viewset import BarbeariaCriarAgendamentoView, CriarAgendamentoView
from .viewsets.agendamento.cancel_viewset import CancelarAgendamentoView
from .viewsets.agendamento.horarios_disponiveis_viewset import HorariosDisponiveisView
from .viewsets.barbearia.endereco_barbearia_viewset import EnderecoBarbeariaPublicView, EnderecoBarbeariaViewSet  
from .viewsets.barbearia.barbearia_viewset import BarbeariaViewSet
from .viewsets.cliente.cliente_agendamentos_viewset import ClienteAgendamentosView
from .viewsets.horario_funcionamento_viewset import HorarioFuncionamentoViewSet
from .viewsets.cliente.cliente_viewset import ClienteViewSet
from .viewsets.cliente.cliente_user_viewset import ClienteLoginView, ClienteUserInfoView
from .viewsets.clientes_da_barbearia_viewset import ClienteDetailView, ClientesDaBarbeariaView
from .viewsets.funcionario_viewset import FuncionarioViewSet
from .viewsets.servico_viewset import ServicoViewSet
from .viewsets.cliente.cliente_reset_password_viewset import PasswordResetRequestView, PasswordResetConfirmView
from .viewsets.barbearia.barbearia_reset_password import BarbeariaPasswordResetRequestView, BarbeariaPasswordResetConfirmView
from .viewsets.barbearia.overview_viewset import OverviewMetricsView
from .viewsets.agendamento.agentamento_viewset import AgendamentoViewSet
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'barbearias', BarbeariaViewSet, basename='barbearia')
router.register(r'barbearia-perfil', BarbeariaPerfilViewSet, basename='barbearia-perfil')
router.register(r'horarios', HorarioFuncionamentoViewSet, basename='horariofuncionamento')
router.register(r'clientes', ClienteViewSet, basename='clientes')
router.register(r'funcionarios', FuncionarioViewSet, basename='funcionario')
router.register(r'servicos', ServicoViewSet, basename='servico')
router.register(r'endereco-barbearia', EnderecoBarbeariaViewSet, basename='endereco-barbearia')
router.register(r'custos', CustoViewSet, basename='custos')
router.register(r'agendamentos', AgendamentoViewSet, basename='agendamento')

urlpatterns = [
    path('clientes/login/', ClienteLoginView.as_view(), name='cliente-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='cliente-token-refresh'),
    path('barbearia/agendamentos/', AgendamentosDaBarbeariaView.as_view(), name='agendamentos-da-barbearia'),
    path('barbearias/update/', BarbeariaPerfilViewSet.as_view({'put': 'update', 'get': 'retrieve'}), name='barbearia-user-info'),
    path("endereco-barbearia-publico/<slug:slug>/", EnderecoBarbeariaPublicView.as_view(), name="endereco-barbearia-publico"),
    path('clientes/user-info/', ClienteUserInfoView.as_view(), name='cliente-user-info'),
    path('clientes/barbearia/<int:barbearia_id>/', ClientesDaBarbeariaView.as_view(), name='clientes-da-barbearia'),
    path('clientes/<int:cliente_id>/', ClienteDetailView.as_view(), name='cliente-detail'),
    path('clientes/agendamentos/', ClienteAgendamentosView.as_view(), name='cliente-agendamentos'),
    path('barbearia/agendamentos/criar/', BarbeariaCriarAgendamentoView.as_view(), name='barbearia-criar-agendamento'),
    path('agendamentos/criar/', CriarAgendamentoView.as_view(), name='criar-agendamento'),
    path('agendamentos/<int:pk>/cancelar/', CancelarAgendamentoView.as_view(), name='cancelar-agendamento'),
    path('agendamentos/horarios-disponiveis/', HorariosDisponiveisView.as_view(), name='horarios_disponiveis'),
    path('clientes/password/reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('clientes/password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('barbearias/password/reset/', BarbeariaPasswordResetRequestView.as_view(), name='barbearia-password-reset-request'),
    path('barbearias/password/reset/confirm/', BarbeariaPasswordResetConfirmView.as_view(), name='barbearia-password-reset-confirm'),
    path('barbearias/overview/', OverviewMetricsView.as_view(), name='overview-metrics'),
    path('', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)