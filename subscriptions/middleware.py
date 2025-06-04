from django.http import HttpResponseForbidden
from django.utils import timezone
from subscriptions.models import Subscription

class SubscriptionAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and hasattr(request.user, 'barbearia'):
            subscription = Subscription.objects.filter(barbearia=request.user.barbearia).first()
            if subscription and not subscription.is_active():
                return HttpResponseForbidden("Seu período de trial expirou. Escolha um plano para continuar.")
        response = self.get_response(request)
        return response