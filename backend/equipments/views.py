from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Equipment
from .serializers import EquipmentSerializer

class EquipmentViewSet(viewsets.ModelViewSet):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_available']
    search_fields = ['name', 'description']

    def destroy(self, request, *args, **kwargs):
        from reservations.models import EquipmentReservation
        equipment = self.get_object()
        
        
        EquipmentReservation.objects.filter(equipment=equipment).delete()
        
       
        equipment.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)