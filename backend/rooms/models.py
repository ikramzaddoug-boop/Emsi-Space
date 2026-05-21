from django.db import models
from django.core.exceptions import ValidationError

class Room(models.Model):
    ROOM_TYPES = (
        ('salle_cours', 'Salle de cours'),
        ('salle_td', 'Salle de TD'),
        ('salle_tp', 'Salle de TP'),
        ('salle_info', 'Salle Informatique'),
        ('amphi', 'Amphi'),
        ('labo', 'Labo'),
        ('atelier', 'Atelier'),
        ('salle_reunion', 'Salle de réunion'),
        ('bureau', 'Bureau'),
        ('autre', 'Autre'),
    )

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    capacity = models.PositiveIntegerField()
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    location = models.CharField(max_length=200, blank=True)
    floor = models.IntegerField(blank=True, null=True)
    is_available = models.BooleanField(default=True)
    image_url = models.URLField(blank=True, null=True, max_length=500)

    equipments = models.ManyToManyField("equipments.Equipment", blank=True, related_name='rooms')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['room_type']),
            models.Index(fields=['is_available']),
        ]

    def clean(self):
        if self.capacity <= 0:
            raise ValidationError("Capacity must be greater than 0.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.get_room_type_display()})"