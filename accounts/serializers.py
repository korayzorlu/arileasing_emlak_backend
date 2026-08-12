import random
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import OTPCode, User
from .sms import SmsSendError, send_sms

OTP_TTL_MINUTES = getattr(settings, "OTP_CODE_TTL_MINUTES", 5)
OTP_MAX_ATTEMPTS = getattr(settings, "OTP_MAX_ATTEMPTS", 5)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "phone_number", "profile_url"]
        read_only_fields = fields


class RequestOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField()

    def validate_phone_number(self, value):
        if not User.objects.filter(phone_number=value, is_active=True).exists():
            raise serializers.ValidationError("Bu telefon numarası sistemde kayıtlı değil.")
        return value

    def save(self):
        phone_number = self.validated_data["phone_number"]
        code = f"{random.randint(0, 999999):06d}"
        otp = OTPCode.objects.create(
            phone_number=phone_number,
            code=code,
            expires_at=timezone.now() + timedelta(minutes=OTP_TTL_MINUTES),
        )
        try:
            send_sms(phone_number, f"Doğrulama kodunuz: {code}. Bu kodu kimseyle paylaşmayın.")
        except SmsSendError:
            otp.delete()
            raise serializers.ValidationError("Kod gönderilemedi. Lütfen daha sonra tekrar deneyin.")


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    code = serializers.CharField()

    def validate(self, attrs):
        phone_number = attrs["phone_number"]
        code = attrs["code"]

        otp = (
            OTPCode.objects.filter(phone_number=phone_number, is_used=False)
            .order_by("-created_at")
            .first()
        )
        if otp is None or otp.is_expired():
            raise serializers.ValidationError("Kod bulunamadı veya süresi doldu.")
        if otp.attempts >= OTP_MAX_ATTEMPTS:
            raise serializers.ValidationError("Çok fazla hatalı deneme. Yeni kod isteyin.")

        if otp.code != code:
            otp.attempts += 1
            otp.save(update_fields=["attempts"])
            raise serializers.ValidationError("Kod hatalı.")

        try:
            user = User.objects.get(phone_number=phone_number, is_active=True)
        except User.DoesNotExist:
            raise serializers.ValidationError("Bu telefon numarası sistemde kayıtlı değil.")

        otp.is_used = True
        otp.save(update_fields=["is_used"])

        refresh = RefreshToken.for_user(user)
        attrs["access"] = str(refresh.access_token)
        attrs["refresh"] = str(refresh)
        attrs["user"] = UserSerializer(user).data
        return attrs
