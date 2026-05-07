from django.test import TestCase
from django.contrib.auth import get_user_model
from rooms.models import Room
from reservations.models import Reservation
from datetime import time, date

User = get_user_model()

class ReservationTestCase(TestCase):
    def setUp(self):
        # Créer un utilisateur
        self.user = User.objects.create_user(
            username="testuser",
            password="123456",
            role="student"
        )
        # Créer une salle
        self.room = Room.objects.create(name="Salle A", capacity=20)

    def test_create_reservation(self):
        reservation = Reservation.objects.create(
            user=self.user,
            room=self.room,
            date=date.today(),
            start_time=time(10, 0),
            end_time=time(12, 0)
        )
        self.assertEqual(reservation.room.name, "Salle A")
        self.assertEqual(reservation.user.username, "testuser")

    def test_conflict_reservation(self):
        # Première réservation
        Reservation.objects.create(
            user=self.user,
            room=self.room,
            date=date.today(),
            start_time=time(10, 0),
            end_time=time(12, 0)
        )
        # Réservation conflictuelle
        with self.assertRaises(Exception):
            Reservation.objects.create(
                user=self.user,
                room=self.room,
                date=date.today(),
                start_time=time(11, 0),
                end_time=time(13, 0)
            )
