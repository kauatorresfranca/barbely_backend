import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.authentication import BarbeariaJWTAuthentication
from users.models import Barbearia
from .models import Subscription
import json
import logging

# Configurar logging para depuração
logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY

@api_view(['POST'])
@csrf_exempt
@authentication_classes([BarbeariaJWTAuthentication])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    if not isinstance(request.user, request.user.__class__.objects.model):
        logger.error(f"User is not a Barbearia: {request.user}")
        return JsonResponse({'error': 'Usuário não é uma barbearia'}, status=401)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        logger.error("Invalid request body: JSON decode failed")
        return JsonResponse({'error': 'Corpo da requisição inválido'}, status=400)

    price_id = data.get('price_id')
    plan_name = data.get('plan_name')
    billing_cycle = data.get('billing_cycle')

    if not price_id or not plan_name or not billing_cycle:
        logger.error(f"Missing required fields: price_id={price_id}, plan_name={plan_name}, billing_cycle={billing_cycle}")
        return JsonResponse(
            {'error': 'price_id, plan_name e billing_cycle são obrigatórios'},
            status=400
        )

    if billing_cycle not in ['monthly', 'yearly']:
        logger.error(f"Invalid billing_cycle: {billing_cycle}")
        return JsonResponse(
            {'error': "billing_cycle deve ser 'monthly' ou 'yearly'"},
            status=400
        )

    try:
        # Verificar se o usuário (Barbearia) existe
        if not Barbearia.objects.filter(id=request.user.id).exists():
            logger.error(f"Barbearia not found for user id: {request.user.id}")
            return JsonResponse({'error': 'Usuário Barbearia não encontrado'}, status=404)

        logger.info(f"Creating checkout session for user: {request.user.id}, email: {request.user.email}")
        
        # Criar um cliente no Stripe
        customer = stripe.Customer.create(
            email=request.user.email,
            metadata={'barbearia_id': str(request.user.id)}
        )
        logger.info(f"Created Stripe customer: {customer.id} with barbearia_id: {request.user.id}")

        # Criar a sessão de checkout
        checkout_session = stripe.checkout.Session.create(
            customer=customer.id,
            payment_method_types=['card'],
            line_items=[{'price': price_id, 'quantity': 1}],
            mode='subscription',
            success_url='http://localhost:5173/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='http://localhost:5173/cancel',
            metadata={'plan_name': plan_name}
        )

        # Criar ou atualizar a assinatura no banco de dados
        subscription, created = Subscription.objects.update_or_create(
            barbearia=request.user,
            defaults={
                'stripe_customer_id': customer.id,
                'plan_name': plan_name,
                'billing_cycle': billing_cycle,
            }
        )
        logger.info(f"Subscription updated/created for barbearia {request.user.id}: {subscription.id}")

        return JsonResponse({'sessionId': checkout_session.id})
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error in create_checkout_session: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        logger.error(f"Error in create_checkout_session: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Erro interno do servidor: ' + str(e)}, status=500)

@api_view(['GET'])
@authentication_classes([BarbeariaJWTAuthentication])
@permission_classes([IsAuthenticated])
def check_session(request, session_id):
    try:
        # Buscar a sessão com os line_items expandidos
        session = stripe.checkout.Session.retrieve(
            session_id,
            expand=['line_items']
        )
        customer_id = session.get('customer')
        subscription_id = session.get('subscription')

        if not customer_id or not subscription_id:
            logger.error(f"Incomplete session: customer_id={customer_id}, subscription_id={subscription_id}")
            return Response({'error': 'Sessão incompleta'}, status=400)

        subscription = stripe.Subscription.retrieve(subscription_id)
        plan_name = session.get('metadata', {}).get('plan_name', "Plano Desconhecido")
        
        # Acessar line_items expandidos
        if not session.line_items or not session.line_items.data:
            logger.error(f"No line items found for session {session_id}")
            return Response({'error': 'Itens da sessão não encontrados'}, status=400)
        
        billing_cycle = "yearly" if session.line_items.data[0].price.recurring.interval == "year" else "monthly"
        status = subscription.status

        customer = stripe.Customer.retrieve(customer_id)
        barbearia_id = customer.metadata.get('barbearia_id')
        logger.info(f"Retrieved customer {customer_id} with barbearia_id: {barbearia_id}")

        if not barbearia_id:
            logger.error(f"No barbearia_id found for customer {customer_id}")
            return Response({'error': 'Barbearia não associada ao cliente'}, status=400)

        try:
            barbearia_id = int(barbearia_id)
            barbearia = Barbearia.objects.get(id=barbearia_id)
            logger.info(f"Found Barbearia with id: {barbearia_id}")
        except (ValueError, TypeError):
            logger.error(f"Invalid barbearia_id format: {barbearia_id}")
            return Response({'error': 'barbearia_id inválido no metadata'}, status=400)
        except Barbearia.DoesNotExist:
            logger.error(f"Barbearia not found for id: {barbearia_id}")
            return Response({'error': f'Barbearia não encontrada para o ID {barbearia_id}'}, status=404)

        subscription_obj, created = Subscription.objects.update_or_create(
            barbearia=barbearia,
            defaults={
                'stripe_customer_id': customer_id,
                'stripe_subscription_id': subscription_id,
                'plan_name': plan_name,
                'billing_cycle': billing_cycle,
                'status': status,
            }
        )
        logger.info(f"Subscription updated/created: {subscription_obj.id}")

        return Response({
            'plan_name': plan_name,
            'billing_cycle': billing_cycle,
            'status': status,
        })
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error in check_session: {str(e)}")
        return Response({'error': str(e)}, status=400)
    except Exception as e:
        logger.error(f"Internal error in check_session: {str(e)}", exc_info=True)
        return Response({'error': f'Erro interno: {str(e)}'}, status=500)

@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        logger.error("Webhook error: Invalid payload")
        return JsonResponse({'error': 'Payload inválido'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Webhook error: Signature verification failed - {str(e)}")
        return JsonResponse({'error': 'Assinatura do webhook inválida'}, status=400)

    event_type = event['type']
    session = event['data']['object']
    customer_id = session.get('customer')
    subscription_id = session.get('subscription')

    try:
        customer = stripe.Customer.retrieve(customer_id)
        barbearia_id = customer.metadata.get('barbearia_id')
        logger.info(f"Webhook: Retrieved customer {customer_id} with barbearia_id: {barbearia_id}")

        if not barbearia_id:
            logger.error(f"No barbearia_id found for customer_id: {customer_id}")
            return JsonResponse({'error': 'Barbearia não associada ao cliente'}, status=400)

        try:
            barbearia_id = int(barbearia_id)
            barbearia = Barbearia.objects.get(id=barbearia_id)
            logger.info(f"Webhook: Found Barbearia with id: {barbearia_id}")
        except (ValueError, TypeError):
            logger.error(f"Webhook: Invalid barbearia_id format: {barbearia_id}")
            return JsonResponse({'error': 'barbearia_id inválido no metadata'}, status=400)
        except Barbearia.DoesNotExist:
            logger.error(f"Webhook: Barbearia not found for id: {barbearia_id}")
            return JsonResponse({'error': f'Barbearia não encontrada para o ID {barbearia_id}'}, status=404)

        if event_type == 'checkout.session.completed':
            subscription = stripe.Subscription.retrieve(subscription_id)
            subscription_obj, created = Subscription.objects.update_or_create(
                barbearia=barbearia,
                defaults={
                    'stripe_customer_id': customer_id,
                    'stripe_subscription_id': subscription_id,
                    'plan_name': session.get('metadata', {}).get('plan_name', "Plano Desconhecido"),
                    'billing_cycle': "yearly" if subscription.items.data[0].price.recurring.interval == "year" else "monthly",
                    'status': 'active',
                }
            )
            logger.info(f"Webhook: Subscription updated/created: {subscription_obj.id}, subscription_id: {subscription_id}")
        elif event_type == 'customer.subscription.updated':
            subscription = stripe.Subscription.retrieve(subscription_id)
            Subscription.objects.filter(stripe_subscription_id=subscription_id).update(
                status=subscription.status
            )
            logger.info(f"Webhook: Subscription updated status to {subscription.status} for subscription_id: {subscription_id}")
        elif event_type == 'customer.subscription.deleted':
            Subscription.objects.filter(stripe_subscription_id=subscription_id).update(
                status='canceled'
            )
            logger.info(f"Webhook: Subscription canceled for subscription_id: {subscription_id}")

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error in webhook: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}", exc_info=True)
        return JsonResponse({'error': 'Erro ao processar o webhook: ' + str(e)}, status=500)

    return JsonResponse({'status': 'success'})