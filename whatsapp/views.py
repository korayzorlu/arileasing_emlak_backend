from django.conf import settings
from rest_framework import exceptions, generics, permissions
from rest_framework.authentication import BaseAuthentication

from .models import WhatsAppMessage
from .serializers import WhatsAppMessageIngestSerializer, WhatsAppMessageSerializer


class IsAdminOrYetkili(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and (user.is_admin or user.is_yetkili))


class WhatsAppMessageListView(generics.ListAPIView):
    serializer_class = WhatsAppMessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrYetkili]
    queryset = WhatsAppMessage.objects.all()


class IngestApiKeyAuthentication(BaseAuthentication):
    """Lets the external system that pushes WhatsApp messages in authenticate with a
    static shared key instead of a user account — there's no end-user behind these calls."""

    def authenticate(self, request):
        key = request.headers.get("X-Api-Key", "")
        expected = getattr(settings, "WHATSAPP_INGEST_API_KEY", "")
        if not expected or key != expected:
            raise exceptions.AuthenticationFailed("Geçersiz API anahtarı.")
        return (None, None)


class WhatsAppMessageIngestView(generics.CreateAPIView):
    serializer_class = WhatsAppMessageIngestSerializer
    authentication_classes = [IngestApiKeyAuthentication]
    permission_classes = [permissions.AllowAny]
