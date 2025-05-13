from datetime import datetime, timedelta
from users.models import HorarioFuncionamento, Agendamento

def calcular_horarios_disponiveis(barbearia, funcionario, data, duracao_servico_em_minutos):
    # Ajustar dia_semana para corresponder ao modelo HorarioFuncionamento (0 = Domingo, 1 = Segunda, ..., 6 = Sábado)
    dia_semana = data.weekday()  # 0 = Segunda, 1 = Terça, ..., 6 = Domingo
    dia_semana_model = (dia_semana + 1) % 7  # Desloca para 0 = Domingo, 1 = Segunda, ..., 6 = Sábado

    try:
        horario_funcionamento = HorarioFuncionamento.objects.get(
            barbearia=barbearia,
            dia_semana=dia_semana_model
        )
    except HorarioFuncionamento.DoesNotExist:
        print(">>> Barbearia não funciona neste dia")
        return []

    if horario_funcionamento.fechado:
        print(">>> Barbearia está fechada neste dia")
        return []

    if not horario_funcionamento.horario_abertura or not horario_funcionamento.horario_fechamento:
        print(">>> Horário de abertura ou fechamento não definido")
        return []

    inicio = datetime.combine(data, horario_funcionamento.horario_abertura)
    fim = datetime.combine(data, horario_funcionamento.horario_fechamento)

    intervalo = timedelta(minutes=30)
    duracao = timedelta(minutes=duracao_servico_em_minutos)

    # Buscar agendamentos do funcionário para o dia
    agendamentos = Agendamento.objects.filter(
        funcionario=funcionario,
        data=data,
        status='CONFIRMADO'
    )

    horarios_ocupados = []
    for agendamento in agendamentos:
        agendamento_inicio = datetime.combine(data, agendamento.hora_inicio)
        agendamento_fim = agendamento_inicio + timedelta(minutes=agendamento.servico.duracao_minutos)
        horarios_ocupados.append((agendamento_inicio, agendamento_fim))

    # Gerar horários disponíveis
    horarios_disponiveis = []
    atual = inicio
    contador = 0
    while atual + duracao <= fim:
        contador += 1
        if contador > 100:
            print("Loop de geração de horários interrompido por segurança.")
            break

        conflito = any(
            (atual < fim_ocupado and atual + duracao > inicio_ocupado)
            for inicio_ocupado, fim_ocupado in horarios_ocupados
        )

        if not conflito:
            horarios_disponiveis.append(atual.strftime('%H:%M'))

        atual += intervalo

    return horarios_disponiveis