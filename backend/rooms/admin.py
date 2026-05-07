from django.contrib import admin
from .models import Room

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'room_type', 'location', 'is_available')
    list_filter = ('room_type', 'is_available', 'created_at')
    search_fields = ('name', 'location')