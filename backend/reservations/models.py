from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from users.models import CustomUser
from rooms.models import Room

class Reservation(models.Model):
    STATUS_CHOICES = (
        ('en_attente', 'Pending'),
        ('confirmee', 'Confirmed'),
        ('annulee', 'Cancelled'),
        ('completee', 'Completed'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reservations')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='reservations')

    date = models.DateField()
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='en_attente'
    )
    
    titre = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    nombre_personnes = models.IntegerField(default=1)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-heure_debut']

    def clean(self):
        if self.heure_debut >= self.heure_fin:
            raise ValidationError("End time must be after start time.")

        if self.date < timezone.now().date():
            raise ValidationError("Cannot book a room in the past.")

        if self.nombre_personnes > self.room.capacity:
            raise ValidationError(
                f"Number of people ({self.nombre_personnes}) exceeds room capacity ({self.room.capacity})."
            )

        conflicts = Reservation.objects.filter(
            room=self.room,
            date=self.date,
            heure_debut__lt=self.heure_fin,
            heure_fin__gt=self.heure_debut,
            status__in=['en_attente', 'confirmee']
        ).exclude(id=self.id)

        if conflicts.exists():
            raise ValidationError("This room is already booked for this time slot.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.room.name} ({self.date})"

    @property
    def duree_heures(self):
        from datetime import datetime
        start = datetime.combine(self.date, self.heure_debut)
        end = datetime.combine(self.date, self.heure_fin)
        duration = (end - start).total_seconds() / 3600
        return duration

    @property
    def est_a_venir(self):
        return self.date >= timezone.now().date()

    @property
    def peut_etre_annulee(self):
        return self.status in ['en_attente', 'confirmee'] and self.est_a_venir