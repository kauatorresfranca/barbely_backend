from django.urls import path
from . import views

urlpatterns = [
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('check-session/<str:session_id>/', views.check_session, name='check_session'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
]