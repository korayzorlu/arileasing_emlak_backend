from django.urls import path

from .views import WhatsAppMessageIngestView, WhatsAppMessageListView

urlpatterns = [
    path("messages/", WhatsAppMessageListView.as_view(), name="whatsapp-messages"),
    path("ingest/", WhatsAppMessageIngestView.as_view(), name="whatsapp-ingest"),
]
