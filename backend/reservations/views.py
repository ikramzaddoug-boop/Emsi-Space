from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime
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
        serializer.save(user=self.request.user)

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