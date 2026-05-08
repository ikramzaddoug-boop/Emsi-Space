from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime, timedelta
from .models import Equipment, EquipmentReservation
from .serializers import EquipmentSerializer, EquipmentReservationSerializer

class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.filter(is_available=True)
    serializer_class = EquipmentSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

    @action(detail=False, methods=['get'])
    def smart_recommendations(self, request):
        """
        AI-powered equipment recommendations based on usage patterns
        """
        from reservations.models import Reservation
        
        # Get query parameters
        activity_type = request.query_params.get('activity_type')
        room_id = request.query_params.get('room_id')
        date_str = request.query_params.get('date')
        
        equipment = Equipment.objects.filter(is_available=True)
        
        # Filter by activity type
        if activity_type:
            equipment = self._filter_by_activity_type(equipment, activity_type)
        
        # Get usage statistics
        equipment_with_stats = []
        for eq in equipment:
            stats = self._get_equipment_stats(eq)
            equipment_with_stats.append({
                'equipment': EquipmentSerializer(eq).data,
                'stats': stats,
                'recommendation_score': self._calculate_equipment_score(eq, activity_type, stats)
            })
        
        # Sort by recommendation score
        equipment_with_stats.sort(key=lambda x: x['recommendation_score'], reverse=True)
        
        return Response({
            'recommendations': equipment_with_stats[:15],
            'total_found': len(equipment_with_stats)
        })

    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """Check equipment availability with smart suggestions"""
        equipment = self.get_object()
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
        
        # Get existing reservations
        reservations = EquipmentReservation.objects.filter(
            equipment=equipment,
            date_debut=date,
            status__in=['en_attente', 'confirmee']
        ).order_by('heure_debut')
        
        booked_slots = [{
            'start': str(r.heure_debut),
            'end': str(r.heure_fin),
            'user': r.user.username
        } for r in reservations]
        
        # Generate smart suggestions
        suggestions = self._suggest_equipment_time_slots(booked_slots)
        
        return Response({
            'equipment': EquipmentSerializer(equipment).data,
            'date': date_str,
            'booked_slots': booked_slots,
            'suggested_slots': suggestions,
            'is_available': len(booked_slots) == 0
        })

    def _filter_by_activity_type(self, equipment, activity_type):
        """Filter equipment based on activity type"""
        activity_mapping = {
            'presentation': ['projector', 'screen', 'microphone', 'speakers'],
            'workshop': ['laptop', 'tools', 'equipment', 'materials'],
            'meeting': ['table', 'chairs', 'whiteboard', 'conference_phone'],
            'lab': ['microscope', 'computer', 'safety_equipment', 'tools'],
            'study': ['desk', 'chair', 'lamp', 'computer']
        }
        
        keywords = activity_mapping.get(activity_type.lower(), [])
        if not keywords:
            return equipment
        
        filtered = []
        for eq in equipment:
            if any(keyword in eq.name.lower() or keyword in (eq.description or '').lower() 
                   for keyword in keywords):
                filtered.append(eq)
        
        return filtered or equipment  # Return all if no matches

    def _get_equipment_stats(self, equipment):
        """Get usage statistics for equipment"""
        past_30_days = datetime.now().date() - timedelta(days=30)
        reservations = EquipmentReservation.objects.filter(
            equipment=equipment,
            date_debut__gte=past_30_days
        )
        
        return {
            'total_reservations': reservations.count(),
            'average_daily_usage': reservations.count() / 30,
            'most_used_hours': self._get_most_used_hours(reservations),
            'reliability_score': self._calculate_reliability_score(equipment, reservations)
        }

    def _calculate_equipment_score(self, equipment, activity_type, stats):
        """Calculate recommendation score for equipment"""
        score = 50  # Base score
        
        # Availability bonus
        if equipment.is_available:
            score += 20
        
        # Quantity bonus (prefer equipment with multiple units)
        if equipment.quantity > 1:
            score += min(equipment.quantity * 5, 15)
        
        # Usage patterns
        if stats['total_reservations'] > 0:
            score += min(stats['total_reservations'], 10)  # Popular equipment bonus
        
        # Reliability bonus
        score += stats['reliability_score'] * 0.3
        
        return min(100, score)

    def _get_most_used_hours(self, reservations):
        """Find most used hours for equipment"""
        hour_counts = {}
        for res in reservations:
            hour = res.heure_debut.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        if hour_counts:
            most_common = max(hour_counts.items(), key=lambda x: x[1])
            return {'hour': most_common[0], 'count': most_common[1]}
        return None

    def _calculate_reliability_score(self, equipment, reservations):
        """Calculate reliability score based on usage vs cancellations"""
        if reservations.count() == 0:
            return 80  # Neutral score for unused equipment
        
        cancelled = reservations.filter(status='annulee').count()
        total = reservations.count()
        
        if total == 0:
            return 80
        
        reliability = ((total - cancelled) / total) * 100
        return min(100, reliability)

    def _suggest_equipment_time_slots(self, booked_slots):
        """Generate smart time suggestions for equipment"""
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


class EquipmentReservationViewSet(viewsets.ModelViewSet):
    serializer_class = EquipmentReservationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'equipment', 'date_debut']
    ordering_fields = ['date_debut', 'heure_debut', 'created_at']
    ordering = ['-date_debut', '-heure_debut']

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return EquipmentReservation.objects.all()
        return EquipmentReservation.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def my_equipment_reservations(self, request):
        reservations = EquipmentReservation.objects.filter(user=request.user)
        serializer = self.get_serializer(reservations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        reservation = self.get_object()
        
        if reservation.user != request.user and not request.user.is_admin:
            return Response(
                {'error': 'You cannot cancel this reservation'},
                status=status.HTTP_403_FORBIDDEN
            )

        if reservation.status not in ['en_attente', 'confirmee']:
            return Response(
                {'error': 'This reservation cannot be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )

        reservation.status = 'annulee'
        reservation.save()
        return Response(
            {'message': 'Equipment reservation cancelled successfully'},
            status=status.HTTP_200_OK
        )