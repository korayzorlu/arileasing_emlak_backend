from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import HttpResponseForbidden, JsonResponse, FileResponse, HttpResponse, response
from django.conf import settings
from asgiref.sync import async_to_sync

from communication.models import WhatsAppContact,WhatsAppMessage

import os
import json
from decimal import Decimal
from datetime import datetime
import requests

class WhatsAppWebhookView(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")

        if mode == "subscribe" and token == settings.WB_VERIFY_TOKEN:
            return HttpResponse(challenge, content_type="text/plain")
        return HttpResponseForbidden()

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        response = requests.post(
            "https://arinet.arileasing.com.tr/api/communication/whatsapp_webhook/",
            headers={"X-Api-Key": settings.EMLAK_WHATSAPP_INGEST_API_KEY},
            json=data,
        )

        print(response.status_code)
        print(response.json())

        return HttpResponse(status=200)