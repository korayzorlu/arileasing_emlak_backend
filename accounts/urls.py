from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import MeView, RegisterView, RequestOTPView, ReviewerLoginView, VerifyOTPView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("otp/request/", RequestOTPView.as_view(), name="auth-otp-request"),
    path("otp/verify/", VerifyOTPView.as_view(), name="auth-otp-verify"),
    path("reviewer-login/", ReviewerLoginView.as_view(), name="auth-reviewer-login"),
    path("refresh/", TokenRefreshView.as_view(), name="auth-refresh"),
    path("me/", MeView.as_view(), name="auth-me"),
]
