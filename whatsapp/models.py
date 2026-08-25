from django.db import models


class WhatsAppMessage(models.Model):
    # Pushed in by an external application, so the format isn't validated against our
    # own +90XXXXXXXXXX rule — whatever that system sends is stored as-is.
    phone_number = models.CharField(max_length=32)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.phone_number} ({self.created_at:%Y-%m-%d %H:%M})"
