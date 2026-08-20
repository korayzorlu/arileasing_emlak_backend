from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


import uuid

phone_validator = RegexValidator(
    regex=r"^\+90[0-9]{10}$",
    message="Telefon numarası +90XXXXXXXXXX formatında olmalıdır.",
)

class EventType(models.TextChoices):
    LOGIN_SUCCESS = "login_success", "Login Success"
    LOGIN_FAILED = "login_failed", "Login Failed"
    LOGOUT = "logout", "Logout"

class FailReason(models.TextChoices):
    BAD_CREDENTIALS = "bad_credentials", "Hatalı kullanıcı adı/şifre"
    INACTIVE = "inactive", "Pasif kullanıcı"
    LOCKED = "locked", "Hesap kilitli"
    OTHER = "other", "Diğer"


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, phone_number, password, **extra_fields):
        if not phone_number:
            raise ValueError("Telefon numarası zorunludur.")
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone_number, password, **extra_fields)

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self._create_user(phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(
        max_length=13, unique=True, validators=[phone_validator]
    )
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    profile_url = models.URLField(blank=True, default="")
    email = models.EmailField(blank=True, default="")
    company_name = models.CharField(max_length=200, blank=True, default="")
    sahibinden_url = models.URLField(blank=True, default="")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.phone_number})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name


class OTPCode(models.Model):
    phone_number = models.CharField(max_length=13, validators=[phone_validator])
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.PositiveSmallIntegerField(default=0)
    is_used = models.BooleanField(default=False)

    class Meta:
        indexes = [models.Index(fields=["phone_number", "is_used"])]

    def is_expired(self) -> bool:
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.phone_number} - {self.code}"

class AuthEvent(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_auth_events",blank=True, null=True)
    event_type =  models.CharField(_("Event Type"), max_length=25, choices=EventType.choices, blank=True, null=True)

    username_attempted  = models.CharField(_("Username Attempt"), max_length=140, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.CharField(_("User Agent"), max_length=500, null=True, blank=True)

    failure_reason =  models.CharField(_("Failure Reason"), max_length=25, choices=FailReason.choices, blank=True, null=True)
    date = models.DateTimeField(_("Date"), auto_now_add=True, null=True)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.event_type) + " | " + str(self.date)