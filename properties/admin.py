from django.contrib import admin

from .models import Property


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "user", "price", "term_months", "down_payment", "created_at"]
    list_filter = ["user"]
    search_fields = ["user__phone_number", "user__first_name", "user__last_name"]
