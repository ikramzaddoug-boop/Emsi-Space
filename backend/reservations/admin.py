from django.contrib import admin
from .models import Reservation

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'date', 'heure_debut', 'heure_fin', 'status')
    list_filter = ('status', 'date', 'room')
    search_fields = ('user__username', 'room__name')