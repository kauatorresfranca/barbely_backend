from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from users.models import HorarioFuncionamento
from users.serializers.horario_funcionamento_serializer import HorarioFuncionamentoSerializer


class HorarioFuncionamentoViewSet(viewsets.ModelViewSet):
    serializer_class = HorarioFuncionamentoSerializer
    queryset = HorarioFuncionamento.objects.all()
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return []  # Deixa público para listagem e detail
        return [IsAuthenticated()]

    def get_queryset(self):
        slug = self.request.query_params.get('slug')
        if slug:
            return HorarioFuncionamento.objects.filter(barbearia__slug=slug)
        return HorarioFuncionamento.objects.none()

    def create(self, request, *args, **kwargs):
        user = request.user

        if not isinstance(request.data, list):
            return Response({"error": "Esperado uma lista de horários."}, status=status.HTTP_400_BAD_REQUEST)

        # Deleta os antigos
        HorarioFuncionamento.objects.filter(barbearia=user).delete()

        # Valida e cria os novos
        instances = []
        for item in request.data:
            item_serializer = self.get_serializer(data=item)
            item_serializer.is_valid(raise_exception=True)
            instance = HorarioFuncionamento(barbearia=user, **item_serializer.validated_data)
            instances.append(instance)

        HorarioFuncionamento.objects.bulk_create(instances)
        return Response(self.get_serializer(instances, many=True).data, status=status.HTTP_201_CREATED)
