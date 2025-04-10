from .agendamento.cancel_viewset import CancelarAgendamentoView
from .agendamento.create_viewset import CriarAgendamentoView
from .agendamento.agendamento_viewset import AgendamentosDaBarbeariaView
from .agendamento.horarios_disponiveis_viewset import calcular_horarios_disponiveis

from .barbearia.barbearia_user_viewset import BarbeariaUserInfoView
from .barbearia.barbearia_viewset import BarbeariaViewSet

from .cliente.cliente_viewset import ClienteViewSet
from .cliente.cliente_user_viewset import ClienteUserInfoView
from .cliente.cliente_user_viewset import ClienteLoginView
from .cliente.cliente_user_viewset import ClienteDetailView