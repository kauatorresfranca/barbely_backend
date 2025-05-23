from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.authentication import BarbeariaJWTAuthentication, ClienteJWTAuthentication
from users.models.cliente.cliente_user import ClienteUser
from users.models import Agendamento, Cliente, Servico
from users.models.funcionario import Funcionario
from users.serializers.agendamento_serializer import CriarAgendamentoSerializer
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from users.utils.utils import generate_random_password
import logging

logger = logging.getLogger(__name__)

class CriarAgendamentoView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [ClienteJWTAuthentication]

    def post(self, request):
        logger.debug(f"Usuário autenticado: {request.user}, Autenticado: {request.user.is_authenticated}")

        # Obter o serviço
        servico_id = request.data.get('servico')
        try:
            servico = Servico.objects.get(id=servico_id)
            logger.debug(f"Serviço encontrado: {servico}")
        except Servico.DoesNotExist:
            logger.error(f"Serviço não encontrado: {servico_id}")
            return Response(
                {"detail": "Serviço não encontrado."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Associar o cliente autenticado
        try:
            cliente_user = request.user
            cliente = Cliente.objects.get(user=cliente_user, barbearia=servico.barbearia)
            logger.debug(f"Cliente encontrado: {cliente}")
        except Cliente.DoesNotExist:
            logger.error(f"Cliente não associado à barbearia: {servico.barbearia}")
            return Response(
                {"detail": "Cliente não associado a esta barbearia."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Adicionar cliente ao payload
        data = request.data.copy()
        data['cliente'] = cliente.id  # Incluir o ID do cliente diretamente
        data['cliente_email'] = cliente_user.email
        data['cliente_nome'] = cliente_user.nome or "Cliente sem nome"

        # Usar o serializer para validar os dados
        serializer = CriarAgendamentoSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Agendamento criado: {serializer.data['id']}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Erros de validação: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BarbeariaCriarAgendamentoView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [BarbeariaJWTAuthentication]

    def post(self, request):
        logger.debug(f"Usuário autenticado: {request.user}, Autenticado: {request.user.is_authenticated}")

        barbearia = request.user
        data = request.data.copy()
        cliente_email = data.get('cliente_email')
        cliente_nome = data.get('cliente_nome')
        telefone = data.get('telefone')  # Optional
        servico_id = data.get('servico')

        if not cliente_email:
            logger.error("E-mail do cliente não fornecido.")
            return Response(
                {"detail": "O e-mail do cliente é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            validate_email(cliente_email)
        except ValidationError:
            logger.error(f"E-mail inválido: {cliente_email}")
            return Response(
                {"detail": "Por favor, forneça um e-mail válido."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not cliente_nome or cliente_nome.strip() == "":
            logger.error("Nome do cliente não fornecido ou vazio.")
            return Response(
                {"detail": "O nome do cliente é obrigatório e não pode ser vazio."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            servico = Servico.objects.get(id=servico_id, barbearia=barbearia)
            logger.debug(f"Serviço encontrado: {servico}")
        except Servico.DoesNotExist:
            logger.error(f"Serviço não encontrado: {servico_id}")
            return Response(
                {"detail": "Serviço não encontrado ou não pertence à barbearia."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            cliente_user = ClienteUser.objects.get(email=cliente_email)
            cliente = Cliente.objects.get(user=cliente_user, barbearia=barbearia)
            if cliente_nome and cliente.user.nome != cliente_nome:
                cliente.user.nome = cliente_nome
                cliente.user.save()
            logger.debug(f"Cliente encontrado: {cliente}")
        except ClienteUser.DoesNotExist:
            try:
                cliente_user = ClienteUser.objects.create_user(
                    email=cliente_email,
                    nome=cliente_nome,
                    password=generate_random_password(),
                    telefone=telefone or None
                )
                cliente = Cliente.objects.create(
                    user=cliente_user,
                    barbearia=barbearia
                )
                logger.info(f"Novo cliente criado: {cliente}")
                # TODO: Enviar e-mail com link de redefinição de senha
            except IntegrityError as e:
                logger.error(f"Erro ao criar ClienteUser: {str(e)}")
                return Response(
                    {"detail": "Não foi possível criar o cliente. Telefone já registrado ou e-mail inválido."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Cliente.DoesNotExist:
            cliente = Cliente.objects.create(
                user=cliente_user,
                barbearia=barbearia
            )
            logger.info(f"Cliente associado à barbearia: {cliente}")

        data['cliente'] = cliente.id

        serializer = CriarAgendamentoSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Agendamento criado: {serializer.data['id']}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Erros de validação: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)