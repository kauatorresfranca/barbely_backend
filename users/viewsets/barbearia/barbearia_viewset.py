from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from users.authentication import BarbeariaJWTAuthentication
from users.models import Barbearia
from users.serializers import BarbeariaSerializer
from rest_framework.permissions import IsAuthenticated
import logging
import cloudinary
from cloudinary.uploader import upload
from django.utils.text import slugify

logger = logging.getLogger(__name__)

class BarbeariaViewSet(viewsets.ModelViewSet):
    queryset = Barbearia.objects.all()
    serializer_class = BarbeariaSerializer
    authentication_classes = [BarbeariaJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['login', 'buscar_por_slug', 'create', 'list', 'metodos_pagamento']:
            return []
        return super().get_permissions()

    @action(detail=False, methods=['post'])
    def login(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        try:
            barbearia = Barbearia.objects.get(email=email)
            if barbearia.check_password(password):
                refresh = RefreshToken.for_user(barbearia)
                refresh.payload['user_type'] = 'barbearia'  # Adiciona user_type ao token
                return Response({
                    "message": "Login realizado com sucesso!",
                    "barbearia_id": barbearia.id,
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                })
            else:
                return Response({"error": "E-mail ou senha inválidos."}, status=status.HTTP_401_UNAUTHORIZED)
        except Barbearia.DoesNotExist:
            return Response({"error": "E-mail ou senha inválidos."}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['get'], url_path='buscar-por-slug/(?P<slug>.+)')
    def buscar_por_slug(self, request, slug=None):
        barbearia = get_object_or_404(Barbearia, slug=slug)
        serializer = BarbeariaSerializer(barbearia)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='metodos-pagamento')
    def metodos_pagamento(self, request):
        slug = request.query_params.get('barbearia_slug')
        if not slug:
            return Response({"error": "Parâmetro 'barbearia_slug' é obrigatório"}, status=status.HTTP_400_BAD_REQUEST)
        barbearia = get_object_or_404(Barbearia, slug=slug)
        data = {
            'pix': barbearia.pix,
            'credit_card': barbearia.credit_card,
            'debit_card': barbearia.debit_card,
            'cash': barbearia.cash
        }
        logger.info(f"Valores retornados em metodos_pagamento (banco): {data}")
        return Response(data)

    def update(self, request, *args, **kwargs):
        barbearia = self.get_object()
        logger.info(f"Dados recebidos para atualização (request.data): {request.data}")

        # Atualiza os campos de pagamento diretamente
        if 'pix' in request.data:
            barbearia.pix = request.data['pix'] == 'true' or request.data['pix'] is True
        if 'credit_card' in request.data:
            barbearia.credit_card = request.data['credit_card'] == 'true' or request.data['credit_card'] is True
        if 'debit_card' in request.data:
            barbearia.debit_card = request.data['debit_card'] == 'true' or request.data['debit_card'] is True
        if 'cash' in request.data:
            barbearia.cash = request.data['cash'] == 'true' or request.data['cash'] is True

        if 'imagem' in request.FILES:
            logger.info(f"Arquivo de imagem recebido: {request.FILES['imagem'].name}")
            try:
                cloudinary.config(
                    cloud_name='dtqpej5qg',
                    api_key='367761293837479',
                    api_secret='zKlny1-C2DTP7rnr0poH-xgmx9U',
                    secure=True
                )
                upload_result = upload(request.FILES['imagem'], folder="barbearias")
                barbearia.imagem = upload_result['secure_url']
                logger.info(f"Imagem enviada para Cloudinary: {barbearia.imagem}")
            except Exception as e:
                logger.error(f"Erro ao enviar imagem para Cloudinary: {str(e)}")
                return Response({"error": f"Erro ao enviar imagem para Cloudinary: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger.warning("Nenhum arquivo 'imagem' encontrado em request.FILES")

        serializer = self.get_serializer(barbearia, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Valores antes do save (banco): pix={Barbearia.objects.get(id=barbearia.id).pix}, credit_card={Barbearia.objects.get(id=barbearia.id).credit_card}, debit_card={Barbearia.objects.get(id=barbearia.id).debit_card}, cash={Barbearia.objects.get(id=barbearia.id).cash}")
            logger.info(f"Valores salvos: pix={barbearia.pix}, credit_card={barbearia.credit_card}, debit_card={barbearia.debit_card}, cash={barbearia.cash}")
            return Response(serializer.data)
        logger.error(f"Erros de validação: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)