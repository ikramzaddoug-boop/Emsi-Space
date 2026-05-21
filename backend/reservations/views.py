from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import models
from django.db.models import Q, Sum
from .models import RoomReservation, EquipmentReservation
from equipments.models import Equipment
from .serializers import RoomReservationSerializer, EquipmentReservationSerializer
from datetime import datetime

class RoomReservationViewSet(viewsets.ModelViewSet):
    serializer_class = RoomReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = RoomReservation.objects.all() if user.is_admin else RoomReservation.objects.filter(user=user)
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    def perform_create(self, serializer):
        # On force les valeurs par défaut pour éviter les erreurs SQL de champ NOT NULL
        serializer.save(
            user=self.request.user,
            status='en_attente'
        )

    @action(detail=False, methods=['post'])
    def ai_analyse(self, request):
        room_id = request.data.get('room')
        date = request.data.get('date')
        start = request.data.get('heure_debut')
        end = request.data.get('heure_fin')

        if not all([room_id, date, start, end]):
            return Response({"error": "Données incomplètes"}, status=400)

        conflits = RoomReservation.objects.filter(
            room_id=room_id, date=date, status__in=['confirmee', 'en_attente']
        ).filter(Q(heure_debut__lt=end, heure_fin__gt=start))

        has_conflict = conflits.exists()
        suggestions = []
        if has_conflict:
            for h in range(8, 18, 2):
                ts, te = f"{h:02d}:00", f"{h+2:02d}:00"
                if not RoomReservation.objects.filter(room_id=room_id, date=date, status__in=['confirmee', 'en_attente']).filter(Q(heure_debut__lt=te, heure_fin__gt=ts)).exists():
                    suggestions.append({"start": ts, "end": te})
                    if len(suggestions) >= 2: break

        return Response({"has_conflict": has_conflict, "suggestions": suggestions})

    @action(detail=False, methods=['get'])
    def statistiques(self, request):
        user = request.user
        # Salles
        if user.is_admin:
            qr = RoomReservation.objects.all()
            qe = EquipmentReservation.objects.all()
        else:
            qr = RoomReservation.objects.filter(user=user)
            qe = EquipmentReservation.objects.filter(user=user)

        total = qr.count() + qe.count()
        confirmees = qr.filter(status='confirmee').count() + qe.filter(status='confirmee').count()
        en_attente = qr.filter(status='en_attente').count() + qe.filter(status='en_attente').count()
        annulees = qr.filter(status='annulee').count() + qe.filter(status='annulee').count()

        # Last 5 reservations for dashboard feed
        recent_rooms = list(qr.order_by('-created_at')[:5].values(
            'id', 'titre', 'date', 'heure_debut', 'status',
            room_name=models.F('room__name')
        ))
        recent_equip = list(qe.order_by('-created_at')[:5].values(
            'id', 'titre', 'date', 'heure_debut', 'status',
            equipment_name=models.F('equipment__name')
        ))

        recent = sorted(
            [{'res_type': 'room', **r} for r in recent_rooms] +
            [{'res_type': 'equipment', **e} for e in recent_equip],
            key=lambda x: x['date'], reverse=True
        )[:5]

        return Response({
            'total': total,
            'confirmees': confirmees,
            'en_attente': en_attente,
            'annulees': annulees,
            'recent': recent,
        })

    @action(detail=False, methods=['get'], url_path='analytics')
    def analytics(self, request):
        from django.db.models import Count
        from django.db.models.functions import TruncMonth, ExtractWeekDay
        from datetime import date, timedelta
        import calendar

        # --- Monthly trend (last 6 months) ---
        today = date.today()
        months_data = []
        for i in range(5, -1, -1):
            # go back i months
            first_of_month = (today.replace(day=1) - timedelta(days=i * 28)).replace(day=1)
            last_of_month_day = calendar.monthrange(first_of_month.year, first_of_month.month)[1]
            last_of_month = first_of_month.replace(day=last_of_month_day)

            room_count = RoomReservation.objects.filter(
                date__range=[first_of_month, last_of_month]
            ).count()
            equip_count = EquipmentReservation.objects.filter(
                date__range=[first_of_month, last_of_month]
            ).count()
            months_data.append({
                'month': first_of_month.strftime('%b %Y'),
                'reservations': room_count + equip_count,
                'salles': room_count,
                'equipements': equip_count,
            })

        # --- Weekly occupancy (current week, Mon-Sun) ---
        day_names = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
        week_start = today - timedelta(days=today.weekday())
        occupancy_by_day = []
        for i in range(7):
            day = week_start + timedelta(days=i)
            count = RoomReservation.objects.filter(date=day, status__in=['confirmee', 'en_attente']).count()
            occupancy_by_day.append({'day': day_names[i], 'rate': count, 'date': str(day)})

        # --- Top rooms ---
        top_rooms = list(
            RoomReservation.objects.values('room__name')
            .annotate(count=Count('id'))
            .order_by('-count')[:8]
        )
        top_rooms = [{'name': r['room__name'] or 'Inconnu', 'count': r['count']} for r in top_rooms]

        # --- Equipment usage ---
        top_equip = list(
            EquipmentReservation.objects.values('equipment__name')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )
        top_equip = [{'name': e['equipment__name'] or 'Inconnu', 'count': e['count']} for e in top_equip]

        return Response({
            'monthly_trend': months_data,
            'occupancy_by_day': occupancy_by_day,
            'top_rooms': top_rooms,
            'top_equipments': top_equip,
        })

class EquipmentReservationViewSet(viewsets.ModelViewSet):
    serializer_class = EquipmentReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = EquipmentReservation.objects.all() if user.is_admin else EquipmentReservation.objects.filter(user=user)
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            status='en_attente'
        )

    @action(detail=False, methods=['post'])
    def ai_analyse(self, request):
        equip_id = request.data.get('equipment')
        date = request.data.get('date')
        start = request.data.get('heure_debut')
        end = request.data.get('heure_fin')

        if not all([equip_id, date, start, end]):
            return Response({"error": "Données incomplètes"}, status=400)

        conflits = EquipmentReservation.objects.filter(
            equipment_id=equip_id, date=date, status__in=['confirmee', 'en_attente']
        ).filter(Q(heure_debut__lt=end, heure_fin__gt=start))

        total_reserve = conflits.aggregate(total=Sum('quantite'))['total'] or 0
        try:
            equip = Equipment.objects.get(id=equip_id)
            has_conflict = total_reserve >= equip.quantity
            available = equip.quantity - total_reserve
        except Equipment.DoesNotExist:
            return Response({"error": "Équipement introuvable"}, status=404)

        return Response({
            "has_conflict": has_conflict, 
            "suggestions": [],
            "available_stock": available
        })