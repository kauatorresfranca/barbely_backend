# users/serializers/cliente_serializer.py
from rest_framework import serializers
from users.models import Cliente, ClienteUser, Agendamento
from users.serializers.agendamento_serializer import AgendamentoSerializer
import logging
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Sum, Count  # Adicione estas importações

logger = logging.getLogger(__name__)

class ClienteUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClienteUser
        fields = ['email', 'nome', 'telefone', 'password', 'date_joined']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'email': {'required': False},
            'nome': {'required': False},
            'telefone': {'required': False},
            'date_joined': {'read_only': True},
        }

    def validate_telefone(self, value):
        import re
        if value and not re.match(r'^\(\d{2}\) \d{5}-\d{4}$', value):
            raise serializers.ValidationError("Telefone deve estar no formato (XX) XXXXX-XXXX.")
        return value

    def validate(self, data):
        logger.debug(f"Validating user data: {data}")
        if self.instance:
            current_email = self.instance.email
            current_telefone = self.instance.telefone

            email = data.get('email')
            if email is not None and email != current_email:
                if ClienteUser.objects.exclude(id=self.instance.id).filter(email=email).exists():
                    raise serializers.ValidationError({"email": "Cliente user with this email already exists."})

            telefone = data.get('telefone')
            if telefone is not None and telefone != current_telefone:
                if ClienteUser.objects.exclude(id=self.instance.id).filter(telefone=telefone).exists():
                    raise serializers.ValidationError({"telefone": "Cliente user with this telefone already exists."})

        return data

class ClienteSerializer(serializers.ModelSerializer):
    user = ClienteUserSerializer(partial=True)
    status = serializers.ChoiceField(choices=Cliente.STATUS_CHOICES, default='ativo')
    historico = serializers.SerializerMethodField()
    estatisticas = serializers.SerializerMethodField()
    saldo = serializers.SerializerMethodField()

    class Meta:
        model = Cliente
        fields = ['id', 'user', 'barbearia', 'imagem', 'status', 'historico', 'estatisticas', 'saldo']
        extra_kwargs = {
            'barbearia': {'required': True},
            'imagem': {'required': False},
        }

    def get_historico(self, obj):
        agendamentos = Agendamento.objects.filter(cliente=obj, status__in=['CONFIRMADO', 'CONCLUIDO']).order_by('-data', '-hora_inicio')[:5]
        return AgendamentoSerializer(agendamentos, many=True).data

    def get_estatisticas(self, obj):
        hoje = timezone.now().date()
        inicio_mes = hoje.replace(day=1)
        
        # Agendamentos este mês
        agendamentos_mes = Agendamento.objects.filter(
            cliente=obj,
            data__gte=inicio_mes,
            status__in=['CONFIRMADO', 'CONCLUIDO']
        ).count()

        # Total de agendamentos
        total_agendamentos = Agendamento.objects.filter(
            cliente=obj,
            status__in=['CONFIRMADO', 'CONCLUIDO']
        ).count()

        # Gasto total
        gasto_total = Agendamento.objects.filter(
            cliente=obj,
            status__in=['CONFIRMADO', 'CONCLUIDO']
        ).aggregate(total=Sum('preco_total'))['total'] or 0  # Use Sum diretamente

        # Último agendamento
        ultimo_agendamento = Agendamento.objects.filter(
            cliente=obj,
            status__in=['CONFIRMADO', 'CONCLUIDO']
        ).order_by('-data', '-hora_inicio').first()
        ultimo_agendamento_data = ultimo_agendamento.data.strftime('%d/%m/%Y') if ultimo_agendamento else 'Nenhum'

        # Serviço mais frequente
        servico_mais_frequente = Agendamento.objects.filter(
            cliente=obj,
            status__in=['CONFIRMADO', 'CONCLUIDO']
        ).values('servico__nome').annotate(count=Count('servico')).order_by('-count').first()  # Use Count diretamente
        servico_mais_frequente_nome = servico_mais_frequente['servico__nome'] if servico_mais_frequente else 'Nenhum'

        return {
            'agendamentos_este_mes': agendamentos_mes,
            'total_agendamentos': total_agendamentos,
            'gasto_total': f"R$ {gasto_total:.2f}",
            'ultimo_agendamento': ultimo_agendamento_data,
            'servico_mais_frequente': servico_mais_frequente_nome,
        }

    def get_saldo(self, obj):
        # Placeholder para saldo (você pode implementar uma lógica real aqui)
        return "R$ 0,00"

    def validate_imagem(self, value):
        logger.debug(f"Validating imagem: {value}")
        if value:
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("A imagem não pode exceder 5MB.")
            if not value.content_type.startswith('image/'):
                raise serializers.ValidationError("O arquivo deve ser uma imagem válida.")
        return value

    def validate(self, data):
        logger.debug(f"Validating data: {data}")
        return data

    def create(self, validated_data):
        logger.debug(f"Creating cliente with data: {validated_data}")
        user_data = validated_data.pop('user')
        password = user_data.pop('password', None)
        user = ClienteUser.objects.create(**user_data)
        if password:
            user.set_password(password)
            user.save()
        cliente = Cliente.objects.create(user=user, **validated_data)
        return cliente

    def update(self, instance, validated_data):
        logger.debug(f"Updating cliente with validated data: {validated_data}")
        user_data = validated_data.pop('user', None)
        if user_data:
            logger.debug(f"Updating user with data: {user_data}")
            user_serializer = ClienteUserSerializer(instance.user, data=user_data, partial=True)
            if user_serializer.is_valid(raise_exception=True):
                user_serializer.save()

        status = validated_data.get('status')
        if status:
            instance.status = status

        for attr, value in validated_data.items():
            if attr != 'user':
                logger.debug(f"Setting {attr} = {value}")
                setattr(instance, attr, value)
        instance.save()
        logger.debug(f"Updated instance: {instance.__dict__}")
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['fotoPerfil'] = instance.imagem.url if instance.imagem else None
        logger.debug(f"Returning representation: {representation}")
        return representation

class ClienteLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        try:
            user = ClienteUser.objects.get(email=email)
        except ClienteUser.DoesNotExist:
            raise serializers.ValidationError("Usuário não encontrado.")

        if not user.check_password(password):
            raise serializers.ValidationError("Senha incorreta.")

        if not user.is_active:
            raise serializers.ValidationError("Conta inativa.")

        try:
            cliente = Cliente.objects.get(user=user)
            if cliente.status == 'inativo':
                raise serializers.ValidationError("Cliente está inativo na barbearia.")
        except Cliente.DoesNotExist:
            raise serializers.ValidationError("Cliente não associado a uma barbearia.")

        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "email": user.email,
                "nome": user.nome,
                "telefone": user.telefone,
                "date_joined": user.date_joined,
                "status": cliente.status
            }
        }