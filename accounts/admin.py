from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import OTPCode, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ["phone_number"]
    list_display = ["phone_number", "first_name", "last_name", "is_staff"]
    search_fields = ["phone_number", "first_name", "last_name"]
    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        ("Kişisel Bilgiler", {"fields": ("first_name", "last_name", "profile_url")}),
        (
            "İzinler",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Önemli Tarihler", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "phone_number",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    readonly_fields = ["date_joined"]


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ["phone_number", "code", "created_at", "expires_at", "attempts", "is_used"]
    search_fields = ["phone_number"]
    readonly_fields = ["created_at"]
