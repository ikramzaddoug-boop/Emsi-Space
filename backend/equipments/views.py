from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Equipment, EquipmentReservation
from .serializers import EquipmentSerializer, EquipmentReservationSerializer

class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.filter(is_available=True)
    serializer_class = EquipmentSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']


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