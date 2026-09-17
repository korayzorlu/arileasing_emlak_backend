from django.urls import path, include

from .views import *

app_name = "communication"

urlpatterns = [
    path('whatsapp_webhook/', WhatsAppWebhookView.as_view(), name="whatsapp_webhook"),


]

