from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import BasePermission

from users.models import HorarioFuncionamento
from users.serializers.barbearia.horario_funcionamento_serializer import HorarioFuncionamentoSerializer

class IsBarbeariaOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.barbearia == request.user

class HorarioFuncionamentoViewSet(viewsets.ModelViewSet):
    serializer_class = HorarioFuncionamentoSerializer
    queryset = HorarioFuncionamento.objects.all()
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return []  # Deixa público para listagem e detail
        return [IsAuthenticated(), IsBarbeariaOwner()]

    def get_queryset(self):
        slug = self.request.query_params.get('slug')
        if slug:
            return HorarioFuncionamento.objects.filter(barbearia__slug=slug)
        return HorarioFuncionamento.objects.none()

    def create(self, request, *args, **kwargs):
        user = request.user

        if not isinstance(request.data, list):
            return Response({"error": "Esperado uma lista de horários."}, status=status.HTTP_400_BAD_REQUEST)

        # Atualizar ou criar os horários
        instances = []
        for item in request.data:
            dia_semana = item.get('dia_semana')
            # Verificar se já existe um horário para o dia
            existing_horario = HorarioFuncionamento.objects.filter(
                barbearia=user, dia_semana=dia_semana
            ).first()
            
            item_serializer = self.get_serializer(data=item)
            item_serializer.is_valid(raise_exception=True)
            
            if existing_horario:
                # Atualizar o registro existente
                for attr, value in item_serializer.validated_data.items():
                    setattr(existing_horario, attr, value)
                existing_horario.save()
                instances.append(existing_horario)
            else:
                # Criar um novo registro
                instance = HorarioFuncionamento(barbearia=user, **item_serializer.validated_data)
                instance.save()
                instances.append(instance)

        return Response(self.get_serializer(instances, many=True).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        slug = self.request.query_params.get('slug')
        dia_semana = request.data.get('dia_semana')

        if not slug or not dia_semana:
            return Response({"error": "Parâmetros 'slug' e 'dia_semana' são obrigatórios."}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar se o horário pertence à barbearia do usuário
        if instance.barbearia.slug != slug:
            return Response({"error": "Horário não pertence à barbearia solicitada."}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)