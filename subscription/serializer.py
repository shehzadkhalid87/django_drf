from rest_framework import serializers


class SubscriptionSerializer(serializers.Serializer):
    price_id = serializers.CharField()
