from rest_framework import serializers
from datetime import datetime
from .models import Reservation
from rooms.serializers import RoomSerializer
from users.serializers import UserSerializer

class ReservationSerializer(serializers.ModelSerializer):
    room_details = RoomSerializer(source='room', read_only=True)
    user_details = UserSerializer(source='user', read_only=True)
    duree_heures = serializers.ReadOnlyField()
    est_a_venir = serializers.ReadOnlyField()
    peut_etre_annulee = serializers.ReadOnlyField()

    class Meta:
        model = Reservation
        fields = [
            'id', 'user', 'user_details', 'room', 'room_details',
            'date', 'heure_debut', 'heure_fin', 'status',
            'titre', 'description', 'nombre_personnes',
            'duree_heures', 'est_a_venir', 'peut_etre_annulee',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def validate(self, data):
        heure_debut = data.get('heure_debut')
        heure_fin = data.get('heure_fin')
        room = data.get('room')
        date = data.get('date')
        nombre_personnes = data.get('nombre_personnes', 1)

        if heure_debut >= heure_fin:
            raise serializers.ValidationError(
                {"heure_fin": "End time must be after start time."}
            )

        if date < datetime.now().date():
            raise serializers.ValidationError(
                {"date": "Cannot book a room in the past."}
            )

        if nombre_personnes > room.capacity:
            raise serializers.ValidationError(
                {"nombre_personnes": f"Number exceeds room capacity ({room.capacity})."}
            )

        conflicts = Reservation.objects.filter(
            room=room,
            date=date,
            heure_debut__lt=heure_fin,
            heure_fin__gt=heure_debut,
            status__in=['en_attente', 'confirmee']
        ).exclude(id=self.instance.id if self.instance else None)

        if conflicts.exists():
            raise serializers.ValidationError(
                {"non_field_errors": "This room is already booked for this time slot."}
            )

        return data