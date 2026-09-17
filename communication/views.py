from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import HttpResponseForbidden, JsonResponse, FileResponse, HttpResponse, response
from django.conf import settings
from asgiref.sync import async_to_sync
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


import os
import json
from decimal import Decimal
from datetime import datetime
import requests
import logging

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name="dispatch")
class WhatsAppWebhookView(View):
    def get(self, request, *args, **kwargs):
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")

        print(mode)
        print(token)
        print(challenge)

        if mode == "subscribe" and token == settings.WB_VERIFY_TOKEN:
            return HttpResponse(challenge, content_type="text/plain")
        return HttpResponseForbidden()

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
    
        logger.info("WA webhook: %s", json.dumps(data, ensure_ascii=False))

        try:
            resp = requests.post(
                "https://arinet.arileasing.com.tr/api/communication/whatsapp_webhook/",
                headers={"X-Api-Key": settings.WHATSAPP_INGEST_API_KEY},
                json=data,
                timeout=10,
            )
            logger.info("arinet forward: status=%s body=%s", resp.status_code, resp.text[:500])
        except Exception:
            logger.exception("arinet forward hatası")
        return HttpResponse(status=200)
