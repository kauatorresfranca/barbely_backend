from rest_framework import viewsets
from .models import Barbearia
from .serializers import BarbeariaSerializer

class BarbeariaViewSet(viewsets.ModelViewSet):
    queryset = Barbearia.objects.all()
    serializer_class = BarbeariaSerializer
