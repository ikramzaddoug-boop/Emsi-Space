from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime, timedelta
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

        # Generate smart time suggestions
        suggestions = self._suggest_time_slots(booked_slots)

        return Response({
            'room': RoomSerializer(room).data,
            'date': date,
            'booked_slots': booked_slots,
            'suggested_slots': suggestions,
            'is_available': len(booked_slots) == 0
        })

    @action(detail=False, methods=['get'])
    def smart_recommendations(self, request):
        """
        AI-powered room recommendations based on user requirements
        """
        from reservations.models import Reservation
        
        # Get query parameters
        capacity = request.query_params.get('capacity')
        room_type = request.query_params.get('room_type')
        date_str = request.query_params.get('date')
        start_time = request.query_params.get('start_time')
        end_time = request.query_params.get('end_time')
        
        rooms = Room.objects.filter(is_available=True)
        
        # Filter by capacity
        if capacity:
            rooms = rooms.filter(capacity__gte=int(capacity))
        
        # Filter by room type
        if room_type:
            rooms = rooms.filter(room_type=room_type)
        
        # Check availability for specific date/time
        if date_str and start_time and end_time:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                start = datetime.strptime(start_time, '%H:%M').time()
                end = datetime.strptime(end_time, '%H:%M').time()
                
                available_rooms = []
                for room in rooms:
                    conflicts = Reservation.objects.filter(
                        room=room,
                        date=date,
                        heure_debut__lt=end,
                        heure_fin__gt=start,
                        status__in=['en_attente', 'confirmee']
                    ).exists()
                    
                    if not conflicts:
                        available_rooms.append(room)
                
                rooms = available_rooms
            except ValueError:
                pass
        
        # Score rooms based on multiple factors
        scored_rooms = []
        for room in rooms:
            score = 0
            
            # Capacity score (prefer rooms that aren't too big)
            if capacity:
                capacity_ratio = room.capacity / int(capacity)
                if 1 <= capacity_ratio <= 1.5:
                    score += 30
                elif capacity_ratio < 1:
                    score += 10
                else:
                    score += 5
            
            # Room type preference
            if room_type == room.room_type:
                score += 20
            
            # Recent usage score
            recent_reservations = Reservation.objects.filter(
                room=room,
                date__gte=datetime.now().date() - timedelta(days=30)
            ).count()
            score += min(recent_reservations * 2, 20)
            
            scored_rooms.append({
                'room': RoomSerializer(room).data,
                'score': score,
                'reasons': self._get_recommendation_reasons(room, capacity, room_type)
            })
        
        # Sort by score and return top recommendations
        scored_rooms.sort(key=lambda x: x['score'], reverse=True)
        
        return Response({
            'recommendations': scored_rooms[:10],
            'total_found': len(scored_rooms)
        })

    def _suggest_time_slots(self, booked_slots):
        """Generate smart time suggestions based on existing bookings"""
        work_hours = [(8, 9), (9, 10), (10, 11), (11, 12), 
                     (14, 15), (15, 16), (16, 17), (17, 18), (18, 19)]
        
        # Convert booked slots to hour blocks
        blocked_hours = set()
        for slot in booked_slots:
            start_hour = int(slot['start'].split(':')[0])
            end_hour = int(slot['end'].split(':')[0])
            for h in range(start_hour, end_hour):
                blocked_hours.add(h)
        
        # Find available slots
        suggestions = []
        for start, end in work_hours:
            if start not in blocked_hours and (end - 1) not in blocked_hours:
                suggestions.append(f"{start:02d}:00 - {end:02d}:00")
                if len(suggestions) >= 4:
                    break
        
        return suggestions

    def _get_recommendation_reasons(self, room, capacity, room_type):
        """Get reasons why this room is recommended"""
        reasons = []
        
        if capacity and room.capacity >= int(capacity):
            if room.capacity <= int(capacity) * 1.5:
                reasons.append("Perfect size for your group")
            else:
                reasons.append("Spacious room available")
        
        if room_type == room.room_type:
            reasons.append("Matches your preferred room type")
        
        if room.capacity >= 50:
            reasons.append("Large capacity room")
        elif room.capacity >= 20:
            reasons.append("Medium capacity room")
        else:
            reasons.append("Intimate setting")
        
        return reasons