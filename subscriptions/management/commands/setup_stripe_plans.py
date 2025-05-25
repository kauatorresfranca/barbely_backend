from django.core.management.base import BaseCommand
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

class Command(BaseCommand):
    help = 'Configura os planos no Stripe'

    def handle(self, *args, **kwargs):
        plans = [
            {
                'name': 'Básico',
                'monthly_price': 4990,  # R$ 49,90 (em centavos)
                'yearly_price': 47990,  # R$ 479,90 (em centavos)
            },
            {
                'name': 'Profissional',
                'monthly_price': 9990,  # R$ 99,90 (em centavos)
                'yearly_price': 95990,  # R$ 959,90 (em centavos)
            },
            {
                'name': 'Premium',
                'monthly_price': 19990,  # R$ 199,90 (em centavos)
                'yearly_price': 191990,  # R$ 1.919,90 (em centavos)
            },
        ]

        for plan in plans:
            try:
                # Criar produto
                product = stripe.Product.create(
                    name=f"Plano {plan['name']}",
                    description=f"Plano {plan['name']} para barbearias",
                )

                # Criar preço mensal
                monthly_price = stripe.Price.create(
                    product=product.id,
                    unit_amount=plan['monthly_price'],
                    currency='brl',
                    recurring={'interval': 'month'},
                )

                # Criar preço anual
                yearly_price = stripe.Price.create(
                    product=product.id,
                    unit_amount=plan['yearly_price'],
                    currency='brl',
                    recurring={'interval': 'year'},
                )

                self.stdout.write(self.style.SUCCESS(
                    f"Plano {plan['name']} criado: Mensal ({monthly_price.id}), Anual ({yearly_price.id})"
                ))
            except stripe.error.StripeError as e:
                self.stdout.write(self.style.ERROR(
                    f"Erro ao criar plano {plan['name']}: {str(e)}"
                ))