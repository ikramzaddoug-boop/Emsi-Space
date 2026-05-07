"""
Run this AFTER migrations:
python manage.py shell < create_demo_data.py
"""

from users.models import CustomUser
from rooms.models import Room
from equipments.models import Equipment

print("Creating demo users...")
CustomUser.objects.all().delete()
admin = CustomUser.objects.create_user(
    username='admin',
    password='admin123',
    email='admin@test.com',
    role='admin'
)
prof = CustomUser.objects.create_user(
    username='prof',
    password='prof123',
    email='prof@test.com',
    role='professeur'
)
student = CustomUser.objects.create_user(
    username='student',
    password='student123',
    email='student@test.com',
    role='etudiant'
)
print(f"✅ Created users: {admin}, {prof}, {student}")

print("\nCreating equipment...")
Equipment.objects.all().delete()
eq1 = Equipment.objects.create(name='Projector', icon='📽️', quantity=3)
eq2 = Equipment.objects.create(name='Whiteboard', icon='📝', quantity=10)
eq3 = Equipment.objects.create(name='Computer', icon='💻', quantity=5)
eq4 = Equipment.objects.create(name='Microphone', icon='🎤', quantity=8)
eq5 = Equipment.objects.create(name='Camera', icon='📷', quantity=2)
print(f"✅ Created {Equipment.objects.count()} equipments")

print("\nCreating rooms...")
Room.objects.all().delete()
r1 = Room.objects.create(
    name='Amphi A',
    capacity=100,
    room_type='amphi',
    location='Building A - Ground Floor'
)
r2 = Room.objects.create(
    name='Class 101',
    capacity=30,
    room_type='class',
    location='Building B - 1st Floor'
)
r3 = Room.objects.create(
    name='Lab 201',
    capacity=20,
    room_type='lab',
    location='Building C - 2nd Floor'
)
r4 = Room.objects.create(
    name='Meeting Room',
    capacity=15,
    room_type='meeting',
    location='Building A - 3rd Floor'
)
print(f"✅ Created {Room.objects.count()} rooms")

print("\n✨ Demo data created successfully!")