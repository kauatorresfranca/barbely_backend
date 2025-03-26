from django.urls import path
from .views import BarbeariaViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'barbearias', BarbeariaViewSet)

urlpatterns = router.urls  # As URLs são geradas automaticamente pelo DRF
