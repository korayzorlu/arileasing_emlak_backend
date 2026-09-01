from rest_framework import serializers

from .models import Property


class PropertySerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=False, allow_blank=True, default="")

    class Meta:
        model = Property
        fields = [
            "id",
            "title",
            "price",
            "term_months",
            "down_payment",
            "listing_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        if not validated_data.get("title"):
            user = validated_data["user"]
            count = Property.objects.filter(user=user).count()
            validated_data["title"] = f"Gayrimenkul {count + 1}"
        return super().create(validated_data)
