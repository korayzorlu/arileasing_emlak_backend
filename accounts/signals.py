from accounts.models import *
from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

def get_client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    return xff.split(",")[0].strip() if xff else request.META.get("REMOTE_ADDR")

@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    AuthEvent.objects.create(
        event_type=EventType.LOGIN_SUCCESS,
        user=user,
        username_attempted=user.get_username(),
        ip_address=get_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:512],
    )

@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    if user is not None:
        AuthEvent.objects.create(
            event_type=EventType.LOGOUT,
            user=user,
            username_attempted=user.get_username(),
            ip_address=get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:512],
        )

@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    AuthEvent.objects.create(
        event_type=EventType.LOGIN_FAILED,
        user=None,
        username_attempted=credentials.get("username", ""),
        ip_address=get_client_ip(request) if request else "0.0.0.0",
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:512] if request else "",
        failure_reason=FailReason.BAD_CREDENTIALS,
    )