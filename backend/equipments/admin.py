from django.contrib import admin
from .models import Equipment, EquipmentReservation

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'is_available', 'created_at')
    list_filter = ('is_available', 'created_at')
    search_fields = ('name',)

@admin.register(EquipmentReservation)
class EquipmentReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'equipment', 'date_debut', 'heure_debut', 'status')
    list_filter = ('status', 'date_debut')
    search_fields = ('user__username', 'equipment__name')