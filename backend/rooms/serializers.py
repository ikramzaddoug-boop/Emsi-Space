from rest_framework import serializers
from .models import Room

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = [
            'id', 'name', 'description', 'capacity', 'room_type',
            'location', 'floor', 'is_available', 'image_url', 'created_at'
        ]