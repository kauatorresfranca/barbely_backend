from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import BasePermission
import logging

from users.authentication import BarbeariaJWTAuthentication
from users.models import HorarioFuncionamento
from users.serializers.barbearia.horario_funcionamento_serializer import HorarioFuncionamentoSerializer

logger = logging.getLogger(__name__)

class IsBarbeariaOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            logger.warning("Usuário não autenticado tentou acessar HorarioFuncionamento.")
            return False
        
        logger.info(f"Tipo de usuário autenticado: {request.user.__class__.__name__}")
        logger.info(f"ID do usuário autenticado: {getattr(request.user, 'id', 'N/A')}")
        logger.info(f"Slug do usuário autenticado: {getattr(request.user, 'slug', 'N/A')}")
        logger.info(f"ID da barbearia associada ao HorarioFuncionamento: {obj.barbearia.id}")
        logger.info(f"Slug da barbearia associada ao HorarioFuncionamento: {obj.barbearia.slug}")
        logger.info(f"Representação do usuário: {repr(request.user)}")
        logger.info(f"Representação da barbearia do horário: {repr(obj.barbearia)}")
        
        is_owner = str(obj.barbearia.id) == str(getattr(request.user, 'id', ''))
        if not is_owner:
            logger.warning(
                f"Usuário {getattr(request.user, 'slug', 'Não autenticado')} "
                f"(ID: {getattr(request.user, 'id', 'N/A')}) "
                f"tentou acessar HorarioFuncionamento de {obj.barbearia.slug} "
                f"(ID: {obj.barbearia.id}) sem permissão."
            )
        return is_owner

class HorarioFuncionamentoViewSet(viewsets.ModelViewSet):
    serializer_class = HorarioFuncionamentoSerializer
    authentication_classes = [BarbeariaJWTAuthentication]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated(), IsBarbeariaOwner()]

    def get_queryset(self):
        user = self.request.user
        slug = self.request.query_params.get('slug')

        if user and user.is_authenticated:
            logger.info(f"Filtrando horários para a barbearia autenticada: {getattr(user, 'slug', 'N/A')}")
            return HorarioFuncionamento.objects.filter(barbearia=user).order_by('dia_semana')

        if slug:
            logger.info(f"Buscando horários para barbearia com slug {slug}")
            return HorarioFuncionamento.objects.filter(barbearia__slug=slug).order_by('dia_semana')

        logger.warning("Nenhum slug ou usuário autenticado fornecido para listar horários.")
        return HorarioFuncionamento.objects.none()

    def get_object(self):
        pk = self.kwargs.get('pk')
        try:
            queryset = self.get_queryset()
            obj = queryset.get(pk=pk)
            return obj
        except HorarioFuncionamento.DoesNotExist:
            logger.error(f"HorarioFuncionamento com ID {pk} não encontrado para o usuário autenticado.")
            return Response(
                {"error": "Horário não encontrado para este ID ou você não tem permissão."},
                status=status.HTTP_404_NOT_FOUND
            )

    def create(self, request, *args, **kwargs):
        user = request.user

        if not isinstance(request.data, list):
            logger.error("Dados inválidos: esperado uma lista de horários.")
            return Response({"error": "Esperado uma lista de horários."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            instances = []
            for item in request.data:
                dia_semana = item.get('dia_semana')
                if dia_semana is None:
                    logger.error("Dados inválidos: 'dia_semana' é obrigatório.")
                    return Response({"error": "'dia_semana' é obrigatório para cada horário."}, status=status.HTTP_400_BAD_REQUEST)

                existing_horario = HorarioFuncionamento.objects.filter(
                    barbearia=user, dia_semana=dia_semana
                ).first()

                item_data = {**item, 'barbearia': user.id}
                item_serializer = self.get_serializer(data=item_data)
                item_serializer.is_valid(raise_exception=True)

                if existing_horario:
                    for attr, value in item_serializer.validated_data.items():
                        setattr(existing_horario, attr, value)
                    existing_horario.save()
                    instances.append(existing_horario)
                else:
                    instance = HorarioFuncionamento(barbearia=user, **item_serializer.validated_data)
                    instance.save()
                    instances.append(instance)

            logger.info(f"Horários salvos com sucesso para a barbearia {getattr(user, 'slug', 'N/A')}.")
            return Response(self.get_serializer(instances, many=True).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Erro ao salvar horários para a barbearia {getattr(user, 'slug', 'N/A')}: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        logger.info(f"Usuário autenticado para PATCH: {getattr(request.user, 'slug', 'Não autenticado')}")
        logger.info(f"Dados recebidos no PATCH: {request.data}")
        instance = self.get_object()
        if isinstance(instance, Response):
            return instance

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            logger.error(f"Erro de validação no PATCH: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        self.perform_update(serializer)

        logger.info(f"Horário atualizado com sucesso para a barbearia {instance.barbearia.slug}, dia {instance.dia_semana}.")
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()