from rest_framework import serializers

from .models import WhatsAppMessage


class WhatsAppMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatsAppMessage
        fields = ["id", "phone_number", "message", "created_at"]
        read_only_fields = ["id", "created_at"]


class WhatsAppMessageIngestSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatsAppMessage
        fields = ["phone_number", "message"]
