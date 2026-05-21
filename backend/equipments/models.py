from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from users.models import CustomUser

class Equipment(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, default='📦')
    photo_url = models.URLField(blank=True, null=True, max_length=500)
    
    quantity = models.PositiveIntegerField(default=1)
    is_available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['is_available']),
        ]

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError("Quantity must be greater than 0.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} (x{self.quantity})"

# Note: EquipmentReservation is removed and merged into reservations.Reservation to match the class diagram.