from rest_framework import serializers
from .models import Equipment, EquipmentReservation
from users.serializers import UserSerializer
from django.utils import timezone

class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Equipment
        fields = ['id', 'name', 'description', 'icon', 'photo_url', 'quantity', 'is_available', 'created_at']


class EquipmentReservationSerializer(serializers.ModelSerializer):
    equipment_details = EquipmentSerializer(source='equipment', read_only=True)
    user_details = UserSerializer(source='user', read_only=True)

    class Meta:
        model = EquipmentReservation
        fields = [
            'id', 'user', 'user_details', 'equipment', 'equipment_details',
            'date_debut', 'heure_debut', 'heure_fin', 'status',
            'titre', 'description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def validate(self, data):
        heure_debut = data.get('heure_debut')
        heure_fin = data.get('heure_fin')
        date_debut = data.get('date_debut')

        if heure_debut >= heure_fin:
            raise serializers.ValidationError(
                {"heure_fin": "End time must be after start time."}
            )

        if date_debut < timezone.now().date():
            raise serializers.ValidationError(
                {"date_debut": "Cannot reserve equipment in the past."}
            )

        equipment = data.get('equipment')
        conflicts = EquipmentReservation.objects.filter(
            equipment=equipment,
            date_debut=date_debut,
            heure_debut__lt=heure_fin,
            heure_fin__gt=heure_debut,
            status__in=['en_attente', 'confirmee']
        ).exclude(id=self.instance.id if self.instance else None)

        if conflicts.exists():
            raise serializers.ValidationError(
                {"non_field_errors": "This equipment is already reserved for this time slot."}
            )

        return data