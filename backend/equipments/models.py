from django.db import models
from django.utils import timezone
from users.models import CustomUser

class Equipment(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, default='📦')
    quantity = models.IntegerField(default=1)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (x{self.quantity})"


class EquipmentReservation(models.Model):
    STATUS_CHOICES = (
        ('en_attente', 'Pending'),
        ('confirmee', 'Confirmed'),
        ('annulee', 'Cancelled'),
        ('completee', 'Completed'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='equipment_reservations')
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='reservations')
    
    date_debut = models.DateField()
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')
    titre = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_debut', '-heure_debut']

    def clean(self):
        from django.core.exceptions import ValidationError
        
        if self.heure_debut >= self.heure_fin:
            raise ValidationError("End time must be after start time")

        if self.date_debut < timezone.now().date():
            raise ValidationError("Cannot reserve equipment in the past")

        conflicts = EquipmentReservation.objects.filter(
            equipment=self.equipment,
            date_debut=self.date_debut,
            heure_debut__lt=self.heure_fin,
            heure_fin__gt=self.heure_debut,
            status__in=['en_attente', 'confirmee']
        ).exclude(id=self.id)

        if conflicts.exists():
            raise ValidationError("This equipment is already reserved for this time slot")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.equipment.name} ({self.date_debut})"