from django.conf import settings
from django.db import models


class Property(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="properties"
    )
    title = models.CharField(max_length=200, blank=True, default="")
    price = models.DecimalField(max_digits=14, decimal_places=2)
    term_months = models.PositiveIntegerField()
    down_payment = models.DecimalField(max_digits=14, decimal_places=2)
    listing_url = models.URLField(max_length=1000, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title or f"{self.price} TRY ({self.term_months} ay) - {self.user}"
