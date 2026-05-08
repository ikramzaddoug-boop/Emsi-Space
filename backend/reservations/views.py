from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
from .models import Reservation
from .serializers import ReservationSerializer

class ReservationViewSet(viewsets.ModelViewSet):
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'room', 'date']
    ordering_fields = ['date', 'heure_debut', 'created_at']
    ordering = ['-date', '-heure_debut']

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Reservation.objects.all()
        return Reservation.objects.filter(user=user)

    def perform_create(self, serializer):
        reservation = serializer.save(user=self.request.user)
        send_mail(
            "Reservation created",
            f"Your reservation for room {reservation.room.name} on {reservation.date} has been created.",
            getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@roombooker.local"),
            [reservation.user.email] if reservation.user.email else [],
            fail_silently=True,
        )

    @action(detail=False, methods=['get'])
    def mes_reservations(self, request):
        reservations = Reservation.objects.filter(user=request.user)
        serializer = self.get_serializer(reservations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def a_venir(self, request):
        today = datetime.now().date()
        reservations = Reservation.objects.filter(
            user=request.user,
            date__gte=today,
            status__in=['en_attente', 'confirmee']
        ).order_by('date', 'heure_debut')
        serializer = self.get_serializer(reservations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def passees(self, request):
        today = datetime.now().date()
        reservations = Reservation.objects.filter(
            user=request.user,
            date__lt=today
        ).order_by('-date', '-heure_debut')
        serializer = self.get_serializer(reservations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def annuler(self, request, pk=None):
        reservation = self.get_object()

        if reservation.user != request.user and not request.user.is_admin:
            return Response(
                {'error': 'You cannot cancel this reservation'},
                status=status.HTTP_403_FORBIDDEN
            )

        if not reservation.peut_etre_annulee:
            return Response(
                {'error': 'This reservation cannot be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )

        reservation.status = 'annulee'
        reservation.save()
        send_mail(
            "Reservation cancelled",
            f"Reservation {reservation.id} has been cancelled.",
            getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@roombooker.local"),
            [reservation.user.email] if reservation.user.email else [],
            fail_silently=True,
        )
        return Response(
            {'message': 'Reservation cancelled successfully'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def confirmer(self, request, pk=None):
        if not request.user.is_admin:
            return Response(
                {'error': 'Only admins can confirm reservations'},
                status=status.HTTP_403_FORBIDDEN
            )

        reservation = self.get_object()
        if reservation.status != 'en_attente':
            return Response(
                {'error': 'Can only confirm pending reservations'},
                status=status.HTTP_400_BAD_REQUEST
            )

        reservation.status = 'confirmee'
        reservation.save()
        send_mail(
            "Reservation confirmed",
            f"Reservation {reservation.id} has been confirmed.",
            getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@roombooker.local"),
            [reservation.user.email] if reservation.user.email else [],
            fail_silently=True,
        )
        return Response(
            ReservationSerializer(reservation).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def statistiques(self, request):
        user = request.user
        
        if user.is_admin:
            total = Reservation.objects.count()
            confirmees = Reservation.objects.filter(status='confirmee').count()
            en_attente = Reservation.objects.filter(status='en_attente').count()
            annulees = Reservation.objects.filter(status='annulee').count()
        else:
            total = Reservation.objects.filter(user=user).count()
            confirmees = Reservation.objects.filter(user=user, status='confirmee').count()
            en_attente = Reservation.objects.filter(user=user, status='en_attente').count()
            annulees = Reservation.objects.filter(user=user, status='annulee').count()

        return Response({
            'total': total,
            'confirmees': confirmees,
            'en_attente': en_attente,
            'annulees': annulees,
        })

    @action(detail=False, methods=['get'])
    def smart_suggestions(self, request):
        """
        AI-powered smart time suggestions for room reservations
        """
        room_id = request.query_params.get('room_id')
        date_str = request.query_params.get('date')
        duration = request.query_params.get('duration', '1')  # Default 1 hour
        
        if not room_id or not date_str:
            return Response(
                {'error': 'room_id and date parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from rooms.models import Room
            room = Room.objects.get(id=room_id, is_available=True)
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            duration_hours = int(duration)
        except (Room.DoesNotExist, ValueError) as e:
            return Response(
                {'error': 'Invalid room_id, date, or duration'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get existing reservations for the room on that date
        existing_reservations = Reservation.objects.filter(
            room=room,
            date=date,
            status__in=['en_attente', 'confirmee']
        ).order_by('heure_debut')
        
        # Generate smart suggestions
        suggestions = self._generate_smart_suggestions(
            existing_reservations, 
            duration_hours
        )
        
        # Analyze booking patterns
        patterns = self._analyze_booking_patterns(room, date)
        
        return Response({
            'room_id': room_id,
            'date': date_str,
            'duration_hours': duration_hours,
            'suggestions': suggestions,
            'patterns': patterns,
            'total_suggestions': len(suggestions)
        })

    @action(detail=False, methods=['post'])
    def check_conflicts(self, request):
        """
        AI-powered conflict detection and alternative suggestions
        """
        room_id = request.data.get('room_id')
        date_str = request.data.get('date')
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')
        
        if not all([room_id, date_str, start_time, end_time]):
            return Response(
                {'error': 'room_id, date, start_time, and end_time are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from rooms.models import Room
            room = Room.objects.get(id=room_id, is_available=True)
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            start = datetime.strptime(start_time, '%H:%M').time()
            end = datetime.strptime(end_time, '%H:%M').time()
        except (Room.DoesNotExist, ValueError) as e:
            return Response(
                {'error': 'Invalid parameters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check for conflicts
        conflicts = Reservation.objects.filter(
            room=room,
            date=date,
            heure_debut__lt=end,
            heure_fin__gt=start,
            status__in=['en_attente', 'confirmee']
        )
        
        if conflicts.exists():
            conflict_details = []
            for conflict in conflicts:
                conflict_details.append({
                    'user': conflict.user.username,
                    'start': str(conflict.heure_debut),
                    'end': str(conflict.heure_fin),
                    'title': conflict.titre or 'No title'
                })
            
            # Generate alternative suggestions
            alternatives = self._suggest_alternative_times(
                room, date, start, end, conflicts
            )
            
            return Response({
                'has_conflicts': True,
                'conflicts': conflict_details,
                'alternatives': alternatives,
                'message': f'This room is already booked during {start_time}-{end_time}. Here are some alternatives:'
            })
        
        return Response({
            'has_conflicts': False,
            'message': 'This time slot is available!'
        })

    def _generate_smart_suggestions(self, existing_reservations, duration_hours):
        """Generate smart time suggestions based on existing bookings"""
        work_hours = [
            (8, 12),   # Morning: 8-12
            (14, 18),  # Afternoon: 14-18
            (18, 20)   # Evening: 18-20
        ]
        
        # Convert existing reservations to blocked time blocks
        blocked_times = []
        for res in existing_reservations:
            start_hour = res.heure_debut.hour
            end_hour = res.heure_fin.hour
            blocked_times.append((start_hour, end_hour))
        
        suggestions = []
        
        for period_start, period_end in work_hours:
            current = period_start
            while current + duration_hours <= period_end:
                # Check if this slot conflicts with existing reservations
                has_conflict = False
                for blocked_start, blocked_end in blocked_times:
                    if not (current + duration_hours <= blocked_start or current >= blocked_end):
                        has_conflict = True
                        break
                
                if not has_conflict:
                    suggestions.append({
                        'start': f"{current:02d}:00",
                        'end': f"{current + duration_hours:02d}:00",
                        'period': self._get_time_period(current),
                        'score': self._calculate_suggestion_score(current, duration_hours)
                    })
                
                current += 1
        
        # Sort by score and return top suggestions
        suggestions.sort(key=lambda x: x['score'], reverse=True)
        return suggestions[:6]

    def _analyze_booking_patterns(self, room, date):
        """Analyze booking patterns for the room"""
        # Get reservations for the past 30 days
        past_date = date - timedelta(days=30)
        recent_reservations = Reservation.objects.filter(
            room=room,
            date__gte=past_date,
            date__lte=date
        )
        
        # Analyze peak hours
        hour_counts = {}
        for res in recent_reservations:
            hour = res.heure_debut.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        peak_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            'total_bookings': recent_reservations.count(),
            'peak_hours': [{'hour': h, 'count': c} for h, c in peak_hours],
            'most_popular_day': self._get_most_popular_day(room, past_date, date)
        }

    def _suggest_alternative_times(self, room, date, start, end, conflicts):
        """Suggest alternative time slots when conflicts occur"""
        duration = end.hour - start.hour
        suggestions = []
        
        # Try same duration at different times
        for hour in range(8, 20 - duration):
            alt_start = datetime.strptime(f"{hour:02d}:00", '%H:%M').time()
            alt_end = datetime.strptime(f"{hour + duration:02d}:00", '%H:%M').time()
            
            # Check if alternative time is available
            alt_conflicts = Reservation.objects.filter(
                room=room,
                date=date,
                heure_debut__lt=alt_end,
                heure_fin__gt=alt_start,
                status__in=['en_attente', 'confirmee']
            )
            
            if not alt_conflicts.exists():
                suggestions.append({
                    'start': str(alt_start),
                    'end': str(alt_end),
                    'reason': 'Same duration, different time'
                })
        
        # Try shorter duration at same time
        for shorter_duration in [1, duration - 1]:
            if shorter_duration > 0:
                alt_end = datetime.strptime(f"{start.hour + shorter_duration:02d}:00", '%H:%M').time()
                
                alt_conflicts = Reservation.objects.filter(
                    room=room,
                    date=date,
                    heure_debut__lt=alt_end,
                    heure_fin__gt=start,
                    status__in=['en_attente', 'confirmee']
                )
                
                if not alt_conflicts.exists():
                    suggestions.append({
                        'start': str(start),
                        'end': str(alt_end),
                        'reason': f'Shorter duration ({shorter_duration} hour)'
                    })
        
        return suggestions[:4]

    def _get_time_period(self, hour):
        """Get time period description"""
        if 6 <= hour < 12:
            return "Morning"
        elif 12 <= hour < 18:
            return "Afternoon"
        else:
            return "Evening"

    def _calculate_suggestion_score(self, hour, duration):
        """Calculate score for a time suggestion"""
        score = 100
        
        # Prefer standard working hours
        if 9 <= hour <= 11:
            score += 20  # Late morning
        elif 14 <= hour <= 16:
            score += 15  # Afternoon
        
        # Prefer reasonable durations
        if 1 <= duration <= 3:
            score += 10
        
        # Avoid very early or very late
        if hour < 8 or hour > 18:
            score -= 20
        
        return max(0, score)

    def _get_most_popular_day(self, room, start_date, end_date):
        """Find the most popular booking day for this room"""
        day_counts = {}
        current = start_date
        while current <= end_date:
            reservations = Reservation.objects.filter(room=room, date=current)
            if reservations.exists():
                day_name = current.strftime('%A')
                day_counts[day_name] = day_counts.get(day_name, 0) + reservations.count()
            current += timedelta(days=1)
        
        if day_counts:
            return max(day_counts.items(), key=lambda x: x[1])
        return None