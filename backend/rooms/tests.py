from django.test import TestCase
from rooms.models import Room, Equipment

class RoomTestCase(TestCase):
    def test_create_room(self):
        room = Room.objects.create(name="Salle B", capacity=30)
        self.assertEqual(room.capacity, 30)

    def test_add_equipment(self):
        room = Room.objects.create(name="Salle C", capacity=15)
        eq = Equipment.objects.create(name="Projecteur")
        room.equipments.add(eq)
        self.assertIn(eq, room.equipments.all())
