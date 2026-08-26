from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import OTPCode, User, AuthEvent, EventType, FailReason


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ["-date_joined"]
    list_display = ["phone_number", "first_name", "last_name", "company_name", "is_approved", "is_admin", "is_yetkili", "is_staff"]
    list_filter = ["is_approved", "is_admin", "is_yetkili", "is_staff", "is_active"]
    search_fields = ["phone_number", "first_name", "last_name"]
    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        (
            "Kişisel Bilgiler",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "company_name",
                    "sahibinden_url",
                    "profile_url",
                )
            },
        ),
        (
            "İzinler",
            {
                "fields": (
                    "is_active",
                    "is_approved",
                    "is_admin",
                    "is_yetkili",
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

@admin.register(AuthEvent)
class AuthEventAdmin(admin.ModelAdmin):
    list_display = ["event_type", "user", "username_attempted", "date", "failure_reason"]
    list_display_links = ["user"]
    search_fields = ["user__username","user__email","user__first_name","user__last_name"]
    list_filter = ["event_type", "failure_reason"]
    inlines = []
    ordering = ["-date"]
    autocomplete_fields = ["user"]

    def user(self,obj):
        return obj.user.username if obj.user else ""

    
    class Meta:
        model = AuthEvent
