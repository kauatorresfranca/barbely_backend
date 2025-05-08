from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from ...models import ClienteUser, Cliente
from ...serializers import ClienteSerializer
from rest_framework.generics import RetrieveAPIView
from users.authentication import ClienteJWTAuthentication

class ClienteLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        senha = request.data.get('senha')

        try:
            user = ClienteUser.objects.get(email=email)
            if user.check_password(senha):
                try:
                    cliente = Cliente.objects.get(user=user)
                    refresh = RefreshToken.for_user(user)
                    refresh.payload['user_type'] = 'cliente'  # Adiciona user_type ao token
                    return Response({
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'cliente_id': cliente.id  # ← usado no front
                    })
                except Cliente.DoesNotExist:
                    return Response({'detail': 'Cliente não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'detail': 'Credenciais inválidas.'}, status=status.HTTP_401_UNAUTHORIZED)
        except ClienteUser.DoesNotExist:
            return Response({'detail': 'Credenciais inválidas.'}, status=status.HTTP_401_UNAUTHORIZED)

class ClienteUserInfoView(APIView):
    authentication_classes = [ClienteJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            cliente = Cliente.objects.get(user=request.user)
            serializer = ClienteSerializer(cliente)
            return Response(serializer.data)
        except Cliente.DoesNotExist:
            return Response({"error": "Cliente não encontrado."}, status=status.HTTP_404_NOT_FOUND)

class ClienteDetailView(RetrieveAPIView):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [AllowAny]