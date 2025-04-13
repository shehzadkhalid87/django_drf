# user.py

from django.urls import path

from .views import (
    ListStripeProducts, StripeCheckoutSession
)
from .webhook import StripeWebhookAPIView

urlpatterns = [
    path('products/list/', ListStripeProducts.as_view(), name='create-customer'),
    path('webhook/', StripeWebhookAPIView.as_view(), name='stripe-webhook'),
    path("checkout/session/", StripeCheckoutSession.as_view(), name="stripe_checkout")
]
