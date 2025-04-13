# user.py

import stripe
from decouple import config
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from core.decorators.api_response import api_response
from core.decorators.authentication import login_required
from core.decorators.get_user_from_request import get_user_from_request

stripe.api_key = config("STRIPE_SID")


class ListStripeProducts(APIView):
    def get(self, request: Request):
        try:
            # List all products from Stripe
            products = stripe.Product.list()

            # For each product, get the associated price
            products_with_prices = []
            for product in products['data']:
                # Fetch prices for the product
                prices = stripe.Price.list(product=product['id'])

                # Include the product details along with price data
                products_with_prices.append({
                    'product': product,
                    'prices': prices['data']  # You can access the first price if you want a single price
                })

            return Response({"data": products_with_prices}, status=200)

        except stripe.error.StripeError as e:
            # Handle Stripe API errors
            return Response({"message": str(e)}, status=500)


class StripeCheckoutSession(APIView):
    @api_response
    @login_required
    @get_user_from_request
    def post(self, request: Request):
        price_id = request.data.get("price_id")
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="subscription",
            line_items=[
                {
                    "price": "price_1Q8gOTSCoubCGBRLVs8cJkj8",
                    "quantity": 1,
                }
            ],
            metadata={
                'user_id': request.user.pk  # Attach user ID to the session metadata
            },
            success_url='https://your-frontend-url.com/success?session_id={CHECKOUT_SESSION_ID}',
            # Replace with your success URL
            cancel_url='https://your-frontend-url.com/cancel',
        )
        return Response({'sessionId': checkout_session.id})
