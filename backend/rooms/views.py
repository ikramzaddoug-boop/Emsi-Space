from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Room
from .serializers import RoomSerializer

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.filter(is_available=True)
    serializer_class = RoomSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['room_type', 'is_available']
    search_fields = ['name', 'location', 'description']
    ordering_fields = ['name', 'capacity', 'created_at']
    ordering = ['name']

    @action(detail=False, methods=['get'])
    def available(self, request):
        rooms = Room.objects.filter(is_available=True)
        serializer = self.get_serializer(rooms, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        from datetime import datetime
        from reservations.models import Reservation
        
        room = self.get_object()
        date_str = request.query_params.get('date')

        if not date_str:
            return Response(
                {'error': 'Date parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )

        reservations = Reservation.objects.filter(
            room=room,
            date=date,
            status__in=['en_attente', 'confirmee']
        ).order_by('heure_debut')

        booked_slots = [{
            'start': str(r.heure_debut),
            'end': str(r.heure_fin),
            'user': r.user.username
        } for r in reservations]

        return Response({
            'room': RoomSerializer(room).data,
            'date': date,
            'booked_slots': booked_slots,
            'is_available': len(booked_slots) == 0
        })