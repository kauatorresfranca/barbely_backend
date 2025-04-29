from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.authentication import BarbeariaJWTAuthentication
from users.models.cliente.cliente_user import ClienteUser
from users.models import Agendamento, Cliente, Servico
from users.models.funcionario import Funcionario
from users.serializers import AgendamentoSerializer
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import IntegrityError
import secrets
import string
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

def generate_random_password(length=16):
    """Generate a secure random password."""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(length))

class CriarAgendamentoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logger.debug(f"Usuário autenticado: {request.user}, Autenticado: {request.user.is_authenticated}")

        if not request.user.is_authenticated:
            logger.error("Usuário não autenticado.")
            return Response(
                {"detail": "Autenticação necessária. Token inválido ou expirado."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        cliente_user = request.user
        logger.debug(f"Usuário: {cliente_user}, Tipo: {type(cliente_user)}")

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

        try:
            cliente = Cliente.objects.get(user=cliente_user, barbearia=servico.barbearia)
            logger.debug(f"Cliente encontrado: {cliente}, Nome: {cliente.user.nome}")
        except Cliente.DoesNotExist:
            logger.info(f"Cliente não registrado para barbearia {servico.barbearia}. Criando associação.")
            cliente = Cliente.objects.create(
                user=cliente_user,
                barbearia=servico.barbearia
            )
            logger.debug(f"Cliente criado: {cliente}")

        data = request.data.copy()
        data['cliente'] = cliente.id

        serializer = AgendamentoSerializer(data=data, context={'request': request})
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
        telefone = data.get('telefone')  # Optional telefone
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

        if not cliente_nome:
            logger.error("Nome do cliente não fornecido.")
            return Response(
                {"detail": "O nome do cliente é obrigatório."},
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
            logger.debug(f"Cliente encontrado: {cliente}")
        except ClienteUser.DoesNotExist:
            try:
                cliente_user = ClienteUser.objects.create_user(
                    email=cliente_email,
                    nome=cliente_nome,
                    password=generate_random_password(),
                    telefone=telefone or None  # Use telefone if provided, else None
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

        serializer = AgendamentoSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Agendamento criado: {serializer.data['id']}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.error(f"Erros de validação: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)