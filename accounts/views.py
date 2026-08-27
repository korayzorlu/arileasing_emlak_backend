from django.contrib.auth import authenticate, login, logout, alogout

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import (
    RegisterSerializer,
    RequestOTPSerializer,
    UserSerializer,
    VerifyOTPSerializer,
)

# Mirrors src/config/reviewerBypass.ts on the frontend. Lets the App Store reviewer log in
# without a real SMS round-trip, but — unlike the old fully-offline sentinel-token version —
# still issues a real JWT for a real account, so every backend-dependent feature (not just
# the login screen) actually works during review instead of silently failing.
REVIEWER_PHONE_NUMBER = "+905542663970"
REVIEWER_OTP_CODE = "681215"


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Kayıt alındı, telefonunuza doğrulama kodu gönderildi."})


class RequestOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        print(request.data)
        whitelist = [
            ''
        ]
        serializer = RequestOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Doğrulama kodu gönderildi."})


class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = authenticate(request, username=data["phone_number"], password='mamtiolen11')
        if user is not None:
            login(request, user)
        return Response(
            {
                "access": data["access"],
                "refresh": data["refresh"],
                "user": data["user"],
            },
            status=status.HTTP_200_OK,
        )


class ReviewerLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        phone_number = request.data.get("phone_number")
        code = request.data.get("code")
        if phone_number != REVIEWER_PHONE_NUMBER or code != REVIEWER_OTP_CODE:
            return Response({"detail": "Geçersiz istek."}, status=status.HTTP_400_BAD_REQUEST)

        user, _ = User.objects.get_or_create(
            phone_number=REVIEWER_PHONE_NUMBER,
            defaults={
                "first_name": "Uygulama",
                "last_name": "İnceleme",
                "email": "inceleme@arileasing.com.tr",
                "company_name": "Arı Leasing Emlak",
                "sahibinden_url": "https://www.sahibinden.com/",
                "is_approved": True,
            },
        )
        if not user.is_approved or not user.is_active:
            user.is_approved = True
            user.is_active = True
            user.save(update_fields=["is_approved", "is_active"])

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data,
            }
        )


class MeView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "patch", "delete", "head", "options"]

    def get_object(self):
        return self.request.user
