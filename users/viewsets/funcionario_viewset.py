from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.authentication import BarbeariaJWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from users.models import Funcionario, Agendamento
from users.serializers.funcionario_serializer import FuncionarioSerializer
from users.serializers.agendamento_serializer import AgendamentoSerializer

class FuncionarioViewSet(viewsets.ModelViewSet):
    serializer_class = FuncionarioSerializer
    queryset = Funcionario.objects.all()
    authentication_classes = [BarbeariaJWTAuthentication]

    def get_permissions(self):
        if self.request.method in ['GET']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        barbearia_slug = self.request.query_params.get('barbearia_slug')

        if user and user.is_authenticated:
            return Funcionario.objects.filter(barbearia=user)

        if barbearia_slug:
            return Funcionario.objects.filter(barbearia__slug=barbearia_slug)

        return Funcionario.objects.none()

    def perform_create(self, serializer):
        serializer.save(barbearia=self.request.user)

    def perform_update(self, serializer):
        serializer.save(barbearia=self.request.user)

    @action(detail=True, methods=['get'], url_path='historico')
    def historico(self, request, pk=None):
        funcionario = self.get_object()
        agendamentos = Agendamento.objects.filter(funcionario=funcionario).order_by('-data', '-hora_inicio')
        serializer = AgendamentoSerializer(agendamentos, many=True)
        return Response(serializer.data)