from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncDate
from datetime import datetime
from users.models import Agendamento, Custo, Cliente, Barbearia, ClienteUser
from users.serializers import OverviewMetricsSerializer
from users.authentication import BarbeariaJWTAuthentication
import logging

logger = logging.getLogger(__name__)

class OverviewMetricsView(APIView):
    authentication_classes = [BarbeariaJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        barbearia = request.user
        if not isinstance(barbearia, Barbearia):
            logger.error(f"Usuário não é uma instância de Barbearia: {barbearia}")
            return Response({"error": "Usuário inválido"}, status=status.HTTP_401_UNAUTHORIZED)

        inicio = request.query_params.get('inicio')
        fim = request.query_params.get('fim')

        try:
            inicio = datetime.strptime(inicio, '%Y-%m-%d').date() if inicio else None
            fim = datetime.strptime(fim, '%Y-%m-%d').date() if fim else None
        except ValueError:
            logger.error("Formato de data inválido")
            return Response({"error": "Formato de data inválido"}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar se é uma requisição para o gráfico
        if request.query_params.get('grafico') == 'vendas':
            agendamentos_concluidos = Agendamento.objects.filter(
                cliente__barbearia=barbearia,
                status='CONCLUIDO'
            )
            if inicio and fim:
                agendamentos_concluidos = agendamentos_concluidos.filter(
                    data__gte=inicio, data__lte=fim
                )

            # Agrupar faturamento por dia
            faturamento_por_dia = agendamentos_concluidos.values('data').annotate(
                total=Sum('preco_total')
            ).order_by('data')

            # Formatar dados para o gráfico no formato YYYY-MM-DD
            data = [
                {
                    'dia': item['data'].strftime('%Y-%m-%d'),
                    'valor': float(item['total'])
                }
                for item in faturamento_por_dia
            ]

            return Response(data, status=status.HTTP_200_OK)

        # Lógica existente para métricas
        agendamentos = Agendamento.objects.filter(cliente__barbearia=barbearia)
        if inicio and fim:
            agendamentos = agendamentos.filter(data__gte=inicio, data__lte=fim)

        agendamentos_concluidos = agendamentos.filter(status='CONCLUIDO')

        faturamento = agendamentos_concluidos.aggregate(total=Sum('preco_total'))['total'] or 0
        clientes_atendidos = agendamentos_concluidos.count()
        agendamentos_count = agendamentos.count()
        ticket_medio = agendamentos_concluidos.aggregate(avg=Avg('preco_total'))['avg'] or 0

        custos = Custo.objects.filter(barbearia=barbearia)
        if inicio and fim:
            custos = custos.filter(data__gte=inicio, data__lte=fim)
        total_custos = custos.aggregate(total=Sum('valor'))['total'] or 0

        total_lucro = faturamento - total_custos

        clientes_novos = 0
        if inicio and fim:
            clientes_users = ClienteUser.objects.filter(
                date_joined__date__gte=inicio,
                date_joined__date__lte=fim
            )
            clientes_novos = Cliente.objects.filter(
                barbearia=barbearia,
                user__in=clientes_users
            ).count()

        data = {
            'faturamento': f'{faturamento:.2f}',
            'total_custos': f'{total_custos:.2f}',
            'total_lucro': f'{total_lucro:.2f}',
            'clientes_atendidos': clientes_atendidos,
            'ticket_medio': f'{ticket_medio:.2f}',
            'agendamentos': agendamentos_count,
            'clientes_novos': clientes_novos,
        }

        serializer = OverviewMetricsSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)