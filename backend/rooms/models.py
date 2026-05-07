from django.db import models

class Room(models.Model):
    ROOM_TYPES = (
        ('amphi', 'Amphitheater'),
        ('class', 'Classroom'),
        ('lab', 'Lab/Workshop'),
        ('meeting', 'Meeting Room'),
    )

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    capacity = models.IntegerField()
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES)
    location = models.CharField(max_length=200, blank=True)
    floor = models.IntegerField(blank=True, null=True)
    is_available = models.BooleanField(default=True)
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_room_type_display()})"