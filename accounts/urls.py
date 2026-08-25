from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import MeView, RegisterView, RequestOTPView, VerifyOTPView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("otp/request/", RequestOTPView.as_view(), name="auth-otp-request"),
    path("otp/verify/", VerifyOTPView.as_view(), name="auth-otp-verify"),
    path("refresh/", TokenRefreshView.as_view(), name="auth-refresh"),
    path("me/", MeView.as_view(), name="auth-me"),
]
