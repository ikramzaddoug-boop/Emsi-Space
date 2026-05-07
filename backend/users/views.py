from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from .models import CustomUser
from .serializers import RegisterSerializer, UserSerializer, UserAdminSerializer

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


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserAdminSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['role', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'department']
    ordering_fields = ['id', 'username', 'email', 'last_login', 'created_at']
    ordering = ['-id']

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return CustomUser.objects.all()
        return CustomUser.objects.filter(id=user.id)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
            token = default_token_generator.make_token(user)
            reset_link = f"http://localhost:5173/reset-password?uid={user.pk}&token={token}"
            send_mail(
                "Room Booker password reset",
                f"Use this link to reset your password: {reset_link}",
                getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@roombooker.local"),
                [email],
                fail_silently=True,
            )
        except CustomUser.DoesNotExist:
            pass

        return Response({"message": "If this email exists, reset instructions have been sent."})


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_id = request.data.get("uid")
        token = request.data.get("token")
        new_password = request.data.get("password")

        if not user_id or not token or not new_password:
            return Response({"error": "uid, token and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "Invalid user"}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"message": "Password reset successful"})