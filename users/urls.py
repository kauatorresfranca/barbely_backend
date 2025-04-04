from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets.barbearia_viewset import BarbeariaViewSet

router = DefaultRouter()
router.register(r'barbearias', BarbeariaViewSet, basename='barbearia')

urlpatterns = [
    path('', include(router.urls)),  # Inclui todas as rotas do ViewSet
]
