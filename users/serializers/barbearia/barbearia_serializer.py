from rest_framework import serializers
from users.models import Barbearia

class BarbeariaSerializer(serializers.ModelSerializer):
    # Definimos 'imagem' como read_only para evitar que o serializer tente validá-lo ou atualizá-lo
    imagem = serializers.CharField(read_only=True)

    class Meta:
        model = Barbearia
        fields = [
            'id', 'nome_barbearia', 'nome_proprietario', 'email', 'username',
            'password', 'cnpj', 'cpf', 'imagem', 'plano', 'data_criacao', 'slug',
            'descricao', 'telefone', 'pix', 'credit_card', 'debit_card', 'cash'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'required': False},
        }

    def create(self, validated_data):
        # Gerando username automaticamente se não for fornecido
        if not validated_data.get('username'):
            base_username = validated_data['nome_proprietario'].lower().replace(" ", "_")
            contador = 1
            new_username = base_username

            while Barbearia.objects.filter(username=new_username).exists():
                new_username = f"{base_username}_{contador}"
                contador += 1

            validated_data['username'] = new_username

        # Criando o usuário com senha criptografada
        senha_plana = validated_data.pop("password", None)
        barbearia = Barbearia(**validated_data)
        if senha_plana:
            barbearia.set_password(senha_plana)
        barbearia.save()
        return barbearia

    def update(self, instance, validated_data):
        # Atualiza os campos de pagamento diretamente
        instance.pix = validated_data.get('pix', instance.pix)
        instance.credit_card = validated_data.get('credit_card', instance.credit_card)
        instance.debit_card = validated_data.get('debit_card', instance.debit_card)
        instance.cash = validated_data.get('cash', instance.cash)

        # Remove campos sensíveis antes de passar ao serializer
        validated_data.pop('password', None)
        validated_data.pop('imagem', None)

        return super().update(instance, validated_data)