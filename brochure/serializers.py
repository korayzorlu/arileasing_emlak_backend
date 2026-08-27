from rest_framework import serializers


class BrochureRequestSerializer(serializers.Serializer):
    price = serializers.IntegerField(min_value=1)
    down_payment = serializers.IntegerField(min_value=0)
    term_months = serializers.IntegerField(min_value=1, max_value=600)
    annual_rate_percent = serializers.FloatField(min_value=0, max_value=100)
