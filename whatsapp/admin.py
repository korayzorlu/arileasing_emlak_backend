from django.contrib import admin

from .models import WhatsAppMessage


@admin.register(WhatsAppMessage)
class WhatsAppMessageAdmin(admin.ModelAdmin):
    list_display = ["phone_number", "created_at"]
    search_fields = ["phone_number", "message"]
    readonly_fields = ["created_at"]
