from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.authentication import BarbeariaJWTAuthentication
from users.serializers import BarbeariaSerializer

class BarbeariaUserInfoView(APIView):
    authentication_classes = [BarbeariaJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        barbearia_user = request.user
        barbearia = getattr(barbearia_user, "barbearia", None)

        if not barbearia:
            return Response({"erro": "Barbearia não encontrada."}, status=404)

        serializer = BarbeariaSerializer(barbearia)
        return Response(serializer.data)
