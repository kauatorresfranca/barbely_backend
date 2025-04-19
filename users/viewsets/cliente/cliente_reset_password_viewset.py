from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from users.models import Cliente, ClientPasswordResetToken
from users.serializers import PasswordResetRequestSerializer, PasswordResetConfirmSerializer

class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            slug = serializer.validated_data.get('slug', '')
            cliente = Cliente.objects.get(user__email=email)
            
            # Criar token de redefinição
            token = ClientPasswordResetToken.objects.create(user=cliente)
            
            # Criar URL de redefinição
            reset_url = f"{settings.FRONTEND_URL}/barbearia/{slug}/reset-password/{token.token}/"
            
            # Enviar e-mail
            subject = 'Redefinir sua senha'
            message = f'Olá, {cliente.user.nome},\n\nClique no link para redefinir sua senha: {reset_url}\n\nEste link expira em 1 hora.'
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            return Response({"message": "E-mail de redefinição enviado."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']
            
            try:
                reset_token = ClientPasswordResetToken.objects.get(token=token)
                if not reset_token.is_valid():
                    return Response({"error": "Token expirado ou inválido."}, status=status.HTTP_400_BAD_REQUEST)
                
                # Atualizar senha no ClienteUser
                cliente = reset_token.user
                cliente.user.set_password(new_password)
                cliente.user.save()
                
                # Deletar token
                reset_token.delete()
                
                return Response({"message": "Senha redefinida com sucesso."}, status=status.HTTP_200_OK)
            except ClientPasswordResetToken.DoesNotExist:
                return Response({"error": "Token inválido."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)