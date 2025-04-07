from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .viewsets.barbearia_viewset import BarbeariaViewSet
from .viewsets.horario_funcionamento_viewset import HorarioFuncionamentoViewSet
from .viewsets.cliente_viewset import ClienteViewSet
from .viewsets.cliente_user_viewset import ClienteLoginView, ClienteUserInfoView
from .viewsets.clientes_da_barbearia_viewset import ClientesDaBarbeariaView
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'barbearias', BarbeariaViewSet, basename='barbearia')
router.register(r'horarios', HorarioFuncionamentoViewSet, basename='horariofuncionamento')
router.register(r'clientes', ClienteViewSet, basename='clientes')

urlpatterns = [
    path('clientes/login/', ClienteLoginView.as_view(), name='cliente-login'),
    path('clientes/token/refresh/', TokenRefreshView.as_view(), name='cliente-token-refresh'),  # <- Adiciona isso
    path('clientes/user-info/', ClienteUserInfoView.as_view(), name='cliente-user-info'),
    path('clientes/barbearia/<int:barbearia_id>/', ClientesDaBarbeariaView.as_view(), name='clientes-da-barbearia'),
    path('', include(router.urls)),
]

