from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from users.views import (
    RegisterView,
    MeView,
    StatsView,
    UserViewSet,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)
from rooms.views import RoomViewSet
from equipments.views import EquipmentViewSet, EquipmentReservationViewSet
from reservations.views import ReservationViewSet

router = DefaultRouter()
router.register(r'rooms', RoomViewSet, basename='room')
router.register(r'equipments', EquipmentViewSet, basename='equipment')
router.register(r'equipment-reservations', EquipmentReservationViewSet, basename='equipment_reservation')
router.register(r'reservations', ReservationViewSet, basename='reservation')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/me/', MeView.as_view(), name='me'),
    path('api/stats/', StatsView.as_view(), name='stats'),
    path('api/password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('api/password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]