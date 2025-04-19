from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from users.models import Barbearia, BarbeariaPasswordResetToken
from users.serializers import BarbeariaPasswordResetRequestSerializer, BarbeariaPasswordResetConfirmSerializer
import logging

logger = logging.getLogger(__name__)

class BarbeariaPasswordResetRequestView(APIView):
    def post(self, request):
        serializer = BarbeariaPasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            barbearia = Barbearia.objects.get(email=email)
            
            # Criar token de redefinição
            token = BarbeariaPasswordResetToken.objects.create(user=barbearia)
            
            # Criar URL de redefinição
            reset_url = f"{settings.FRONTEND_URL}/reset-password-barbearia/{token.token}/"
            
            # Enviar e-mail
            subject = 'Redefinir sua senha'
            message = f'Olá, {barbearia.nome_barbearia},\n\nClique no link para redefinir sua senha: {reset_url}\n\nEste link expira em 1 hora.'
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            logger.info(f"E-mail de redefinição enviado para: {email}")
            return Response({"message": "E-mail de redefinição enviado."}, status=status.HTTP_200_OK)
        logger.error(f"Erro na validação do serializer: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BarbeariaPasswordResetConfirmView(APIView):
    def post(self, request):
        logger.debug(f"Requisição recebida: {request.data}")
        serializer = BarbeariaPasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']
            
            try:
                reset_token = BarbeariaPasswordResetToken.objects.get(token=token)
                if not reset_token.is_valid():
                    logger.warning(f"Token expirado: {token}")
                    return Response({"error": "Token expirado ou inválido."}, status=status.HTTP_400_BAD_REQUEST)
                
                # Atualizar senha
                barbearia = reset_token.user
                barbearia.set_password(new_password)
                barbearia.save()
                
                # Deletar token
                reset_token.delete()
                
                logger.info(f"Senha redefinida com sucesso para a barbearia: {barbearia.email}")
                return Response({"message": "Senha redefinida com sucesso."}, status=status.HTTP_200_OK)
            except BarbeariaPasswordResetToken.DoesNotExist:
                logger.warning(f"Token inválido: {token}")
                return Response({"error": "Token inválido."}, status=status.HTTP_400_BAD_REQUEST)
        logger.error(f"Erro na validação do serializer: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)