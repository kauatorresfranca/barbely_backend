from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.viewsets.agendamento.agendamento_viewset import AgendamentosDaBarbeariaView
from users.viewsets.agendamento.atualizar_status import AtualizarStatusAgendamentosView
from users.viewsets.barbearia.barbearia_perfil_viewset import BarbeariaPerfilViewSet
from users.viewsets.agendamento.create_viewset import CriarAgendamentoView
from users.viewsets.agendamento.cancel_viewset import CancelarAgendamentoView
from users.viewsets.agendamento.horarios_disponiveis_viewset import HorariosDisponiveisView
from users.viewsets.barbearia.endereco_barbearia_viewset import EnderecoBarbeariaPublicView, EnderecoBarbeariaViewSet  
from users.viewsets.barbearia.barbearia_viewset import BarbeariaViewSet
from users.viewsets.barbearia.barbearia_perfil_viewset import BarbeariaPerfilViewSet
from users.viewsets.cliente.cliente_agendamentos_viewset import ClienteAgendamentosView
from users.viewsets.horario_funcionamento_viewset import HorarioFuncionamentoViewSet
from users.viewsets.cliente.cliente_viewset import ClienteViewSet
from users.viewsets.cliente.cliente_user_viewset import ClienteLoginView, ClienteUserInfoView
from users.viewsets.clientes_da_barbearia_viewset import ClientesDaBarbeariaView
from users.viewsets.funcionario_viewset import FuncionarioViewSet
from users.viewsets.servico_viewset import ServicoViewSet

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

urlpatterns = [
    path('clientes/login/', ClienteLoginView.as_view(), name='cliente-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='cliente-token-refresh'),
    path('barbearia/agendamentos/', AgendamentosDaBarbeariaView.as_view(), name='agendamentos-da-barbearia'),
    path('barbearias/update/', BarbeariaPerfilViewSet.as_view({'put': 'update', 'get': 'retrieve'}), name='barbearia-user-info'),
    path("endereco-barbearia-publico/<slug:slug>/", EnderecoBarbeariaPublicView.as_view(), name="endereco-barbearia-publico"),
    path('clientes/user-info/', ClienteUserInfoView.as_view(), name='cliente-user-info'),
    path('clientes/barbearia/<int:barbearia_id>/', ClientesDaBarbeariaView.as_view(), name='clientes-da-barbearia'),
    path('clientes/agendamentos/', ClienteAgendamentosView.as_view(), name='cliente-agendamentos'),
    path('agendamentos/criar/', CriarAgendamentoView.as_view(), name='criar-agendamento'),
    path('agendamentos/<int:pk>/cancelar/', CancelarAgendamentoView.as_view(), name='cancelar-agendamento'),
    path('agendamentos/horarios-disponiveis/', HorariosDisponiveisView.as_view(), name='horarios_disponiveis'),
    path('agendamentos/atualizar-status/', AtualizarStatusAgendamentosView.as_view(), name='atualizar-status-agendamentos'),
    path('', include(router.urls)),
]

# ✅ Serve arquivos de mídia em modo de desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
