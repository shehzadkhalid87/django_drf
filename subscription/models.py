from django.db import models

from auth_app.models.user import UserEntity
from core.enums.enums import SUBSCRIPTION_STATUS


# Create your models here.
class SubscriptionEntity(models.Model):
    user_id = models.OneToOneField(UserEntity, on_delete=models.CASCADE, null=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)
    last_charged = models.DateTimeField(null=True),
    status = models.CharField(max_length=128, choices=SUBSCRIPTION_STATUS.choices(),
                              default=SUBSCRIPTION_STATUS.CREATED.value[0])
    card_brand = models.CharField(max_length=128, null=True)
    card_last4 = models.CharField(max_length=128, null=True)
    card_exp_month = models.CharField(max_length=128, null=True)
    card_exp_year = models.CharField(max_length=128, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_subscription"
