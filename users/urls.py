from django.urls import path
from .viewsets.barbearia_viewset import BarbeariaViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'barbearias', BarbeariaViewSet, basename='barbearia')

urlpatterns = [
    path('login/', BarbeariaViewSet.as_view({'post': 'login'}), name='login'),
]

urlpatterns += router.urls
