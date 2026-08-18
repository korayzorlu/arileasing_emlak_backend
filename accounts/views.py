from django.contrib.auth import authenticate, login, logout, alogout

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RequestOTPSerializer, UserSerializer, VerifyOTPSerializer


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

        user = authenticate(request, username=data["phone_number"])
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


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
