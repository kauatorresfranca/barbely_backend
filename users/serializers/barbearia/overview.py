from rest_framework import serializers

class OverviewMetricsSerializer(serializers.Serializer):
    faturamento = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_custos = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_lucro = serializers.DecimalField(max_digits=10, decimal_places=2)
    clientes_atendidos = serializers.IntegerField()
    ticket_medio = serializers.DecimalField(max_digits=10, decimal_places=2)
    agendamentos = serializers.IntegerField()
    clientes_novos = serializers.IntegerField()