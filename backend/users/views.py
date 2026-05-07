from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CustomUser
from .serializers import RegisterSerializer, UserSerializer

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'user': UserSerializer(user).data,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(request.user).data)


class StatsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        from reservations.models import Reservation
        from rooms.models import Room
        from equipments.models import Equipment
        
        return Response({
            'total_rooms': Room.objects.count(),
            'total_equipments': Equipment.objects.count(),
            'total_reservations': Reservation.objects.count(),
            'occupation_rate': self.calculate_occupation_rate(),
        })

    def calculate_occupation_rate(self):
        from datetime import datetime, timedelta
        from reservations.models import Reservation
        from rooms.models import Room
        
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        reservations = Reservation.objects.filter(
            date__range=[week_start, week_end],
            status__in=['en_attente', 'confirmee']
        ).count()
        
        total_rooms = Room.objects.count()
        if total_rooms == 0:
            return 0
        
        max_possible = total_rooms * 7 * 24
        return int((reservations / max_possible) * 100) if max_possible > 0 else 0