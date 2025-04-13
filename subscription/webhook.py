# webhook.py

import logging

import stripe
from decouple import config
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView

from auth_app.repositories.user import UserRepository
from core.enums import SUBSCRIPTION_STATUS
from subscription.service import SubscriptionService

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookAPIView(APIView):
    def post(self, request):
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, config("STRIPE_WEBHOOK_SECRET"))
        except ValueError:
            return JsonResponse({'status': 'invalid payload'}, status=400)
        except stripe.error.SignatureVerificationError:
            return JsonResponse({'status': 'invalid signature'}, status=400)

        print("EVENT -> ", event["type"])

        if event["type"] == 'checkout.session.completed':
            session = event['data']['object']
            user_id = session['metadata']['user_id']
            customer_id = session['customer']
            user = UserRepository.find_one_by_id(user_id=int(user_id))
            db_sub = SubscriptionService.find_one("stripe_customer_id", customer_id)
            if db_sub is None:
                SubscriptionService.create(
                    {
                        "stripe_customer_id": customer_id,
                        "user_id": user,
                        "status": SUBSCRIPTION_STATUS.CREATED.value[0]
                    }
                )
            else:
                db_sub.user_id = user
                db_sub.status = SUBSCRIPTION_STATUS.PENDING.value[0]
                db_sub.save()
        elif event["type"] == 'customer.subscription.created':
            subscription = event['data']['object']
            customer_id = subscription['customer']
            subscription_id = subscription['id']

            db_sub = SubscriptionService.find_one_q(stripe_customer_id=customer_id,
                                                    stripe_subscription_id=subscription_id)
            # Find if subscription exists
            if db_sub is None:
                logger.info(f"Creating customer with id {customer_id} and with subscription id {subscription_id}")
                print(f"Creating customer with id {customer_id} and with subscription id {subscription_id}")
                SubscriptionService.create(
                    {
                        "stripe_customer_id": customer_id,
                        "stripe_subscription_id": subscription_id,
                        "status": SUBSCRIPTION_STATUS.CREATED.value[0]
                    }
                )
        # Handle other events like payment succeeded/failed
        elif event['type'] == 'invoice.payment_succeeded':
            invoice = event['data']['object']
            customer_id = invoice['customer']
            payment_intent_id = invoice['payment_intent']

            # Retrieve the subscription associated with the invoice
            subscription_id = invoice['subscription']
            print("SUBS => ", subscription_id)
            db_sub = SubscriptionService.find_one("stripe_customer_id", customer_id)

            if db_sub:
                # Retrieve the payment intent details from Stripe
                payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

                # Extract the necessary payment details
                card_brand = payment_intent.charges.data[0].payment_method_details.card.brand
                card_last4 = payment_intent.charges.data[0].payment_method_details.card.last4
                card_exp_month = payment_intent.charges.data[0].payment_method_details.card.exp_month
                card_exp_year = payment_intent.charges.data[0].payment_method_details.card.exp_year

                # Update the subscription with payment details
                db_sub.card_brand = card_brand
                db_sub.card_last4 = card_last4
                db_sub.card_exp_month = card_exp_month
                db_sub.card_exp_year = card_exp_year
                db_sub.status = SUBSCRIPTION_STATUS.PAID.value[0]
                db_sub.save()

        elif event['type'] == 'invoice.payment_failed':
            # Handle failed payment logic
            pass

        return JsonResponse({'status': 'success'}, status=200)


def handle_successful_payment(invoice):
    # Logic to update the user's subscription status
    pass


def handle_failed_payment(invoice):
    # Logic to notify the user of the failed payment
    pass

# EVENT ->  customer.updated
# EVENT ->  customer.subscription.created
# EVENT ->  customer.updated
# EVENT ->  payment_intent.created
# EVENT ->  customer.created
# EVENT ->  invoice.created
# EVENT ->  payment_intent.requires_action
# EVENT ->  invoice.finalized
# EVENT ->  invoice.payment_failed
# EVENT ->  invoice.payment_action_required
# EVENT ->  invoice.updated
# EVENT ->  charge.succeeded
# EVENT ->  invoice.updated
# EVENT ->  customer.subscription.updated
# EVENT ->  checkout.session.completed
# EVENT ->  customer.updated
# EVENT ->  payment_intent.succeeded
# EVENT ->  invoice.paid
# EVENT ->  invoice.payment_succeeded
# EVENT ->  payment_method.attached
