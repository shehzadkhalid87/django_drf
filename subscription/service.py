from typing import Dict, Any, Union

from .models import SubscriptionEntity


class SubscriptionService:

    @staticmethod
    def create(data: Dict[str, Any]) -> SubscriptionEntity:
        return SubscriptionEntity.objects.create(**data)

    @staticmethod
    def find_one(key: str, value: Any) -> Union['SubscriptionEntity', None]:
        return SubscriptionEntity.objects.filter(**{key: value}).first()

    @staticmethod
    def find_one_q(**kwargs: Any) -> Union['SubscriptionEntity', None]:
        """
        Find a single SubscriptionEntity based on multiple filter criteria.

        :param kwargs: Field-value pairs to filter on (e.g., user_id=1, stripe_customer_id='cus_xxx').
        :return: SubscriptionEntity instance or None if not found.
        """
        return SubscriptionEntity.objects.filter(**kwargs).first()

    @staticmethod
    def update(subscription: SubscriptionEntity, data: Dict[str, Any]) -> SubscriptionEntity:
        for key, value in data.items():
            if hasattr(data, key):
                setattr(data, key, value)
        subscription.save()
        return subscription
