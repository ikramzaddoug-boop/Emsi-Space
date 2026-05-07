from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from users.views import RegisterView, MeView, StatsView
from rooms.views import RoomViewSet
from equipments.views import EquipmentViewSet, EquipmentReservationViewSet
from reservations.views import ReservationViewSet

router = DefaultRouter()
router.register(r'salles', RoomViewSet, basename='room')
router.register(r'equipements', EquipmentViewSet, basename='equipment')
router.register(r'reservations-equipement', EquipmentReservationViewSet, basename='equipment_reservation')
router.register(r'reservations', ReservationViewSet, basename='reservation')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    path('api/inscription/', RegisterView.as_view(), name='register'),
    path('api/moi/', MeView.as_view(), name='me'),
    path('api/statistiques/', StatsView.as_view(), name='stats'),
]