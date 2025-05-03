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
        if self.action in ['login', 'buscar_por_slug', 'create', 'list']:
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
                return Response({
                    "message": "Login realizado com sucesso!",
                    "barbearia_id": barbearia.id,
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
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

    def update(self, request, *args, **kwargs):
        barbearia = self.get_object()
        logger.info(f"Dados recebidos para atualização (request.data): {request.data}")
        logger.info(f"Arquivos recebidos (request.FILES): {dict(request.FILES)}")
        logger.info(f"Conteúdo de request.FILES.items(): {list(request.FILES.items())}")
        logger.info(f"request.FILES está vazio? {len(request.FILES) == 0}")

        # Cria uma cópia dos dados para o serializer, excluindo a chave 'imagem'
        data_to_serialize = {key: value for key, value in request.data.items() if key != 'imagem'}
        logger.info(f"Dados para o serializer (sem imagem): {data_to_serialize}")

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

        serializer = self.get_serializer(barbearia, data=data_to_serialize, partial=True)
        if serializer.is_valid():
            barbearia = serializer.save()
            if 'nome_barbearia' in request.data:
                novo_slug = slugify(request.data['nome_barbearia'])
                barbearia.slug = novo_slug
            if 'username' in request.data:
                barbearia.username = request.data['username']
            barbearia.save()
            logger.info(f"Barbearia atualizada com sucesso: {serializer.data}")
            return Response(serializer.data)
        logger.error(f"Erros de validação: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)