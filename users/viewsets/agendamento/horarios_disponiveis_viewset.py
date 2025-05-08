from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from datetime import datetime
from users.models import Funcionario, Servico, HorarioFuncionamento, Barbearia
from users.utils.calcular_horarios_disponiveis import calcular_horarios_disponiveis
import logging

logger = logging.getLogger(__name__)

class HorariosDisponiveisView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        funcionario_id = request.GET.get('funcionario')
        data_str = request.GET.get('data')
        servico_id = request.GET.get('servico')
        slug = request.GET.get('slug')  # Parâmetro opcional para validação

        if not funcionario_id or not data_str or not servico_id:
            return Response(
                {'erro': 'Parâmetros "funcionario", "data" e "servico" são obrigatórios.'},
                status=400
            )

        try:
            data = datetime.strptime(data_str, '%Y-%m-%d').date()
            dia_semana = data.weekday()  # 0 = Segunda, 1 = Terça, ..., 6 = Domingo
            # Ajustar para o modelo HorarioFuncionamento (0 = Domingo, 1 = Segunda, ...)
            dia_semana_model = dia_semana if dia_semana < 6 else 0  # Domingo deve ser 0

            funcionario = Funcionario.objects.get(id=int(funcionario_id))
            servico = Servico.objects.get(id=int(servico_id), barbearia=funcionario.barbearia)

            # Validação opcional com slug
            if slug and funcionario.barbearia.slug != slug:
                return Response({'erro': 'Barbearia do funcionário não corresponde ao slug.'}, status=400)

            horarios = calcular_horarios_disponiveis(
                funcionario.barbearia, funcionario, data, servico.duracao_minutos
            )
            logger.info(f"Horários disponíveis para data {data_str}: {horarios}")
            return Response({'horarios_disponiveis': horarios})

        except ValueError:
            return Response({'erro': 'Data inválida. Use o formato YYYY-MM-DD.'}, status=400)
        except Funcionario.DoesNotExist:
            return Response({'erro': 'Funcionário não encontrado.'}, status=404)
        except Servico.DoesNotExist:
            return Response({'erro': 'Serviço não encontrado ou não pertence à barbearia do funcionário.'}, status=404)
        except Exception as e:
            logger.error(f"Erro ao calcular horários: {str(e)}")
            return Response({'erro': str(e)}, status=500)