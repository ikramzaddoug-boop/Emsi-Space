"""
Management command: python manage.py seed_data
Injects complete demo data for EmsiSpace (users, rooms, equipment, reservations).
"""

import os
import django
from datetime import date, time, timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from users.models import CustomUser
from rooms.models import Room
from equipments.models import Equipment
from reservations.models import RoomReservation, EquipmentReservation


print("\n🚀 [SEED] Starting EmsiSpace demo data...\n")


# ─────────────────────────────────────────────
# 1. USERS
# ─────────────────────────────────────────────
users_data = [
    {"username": "admin_emsi", "email": "admin@emsi.ma", "password": "Admin1234!", "role": "admin",
     "first_name": "Admin", "last_name": "EMSI", "department": "Direction"},

    {"username": "prof_rachid", "email": "rachid@emsi.ma", "password": "Prof1234!", "role": "professor",
     "first_name": "Rachid", "last_name": "Benali", "department": "Informatique"},

    {"username": "prof_imane", "email": "imane@emsi.ma", "password": "Prof1234!", "role": "professor",
     "first_name": "Imane", "last_name": "Elfarissi", "department": "Réseaux"},

    {"username": "etudiant_ali", "email": "ali@emsi.ma", "password": "Etud1234!", "role": "student",
     "first_name": "Ali", "last_name": "Moussaoui", "department": "Génie Logiciel"},

    {"username": "etudiant_aya", "email": "aya@emsi.ma", "password": "Etud1234!", "role": "student",
     "first_name": "Aya", "last_name": "Khalil", "department": "Data Science"},

    {"username": "etudiant_omar", "email": "omar@emsi.ma", "password": "Etud1234!", "role": "student",
     "first_name": "Omar", "last_name": "Tazi", "department": "Cybersécurité"},
]

users = {}

for u in users_data:
    user, created = CustomUser.objects.get_or_create(
        username=u["username"],
        defaults={
            "email": u["email"],
            "role": u["role"],
            "first_name": u["first_name"],
            "last_name": u["last_name"],
            "department": u["department"],
        }
    )

    if created:
        user.set_password(u["password"])
        user.save()
        print(f"  ✅ Created user: {u['username']}")
    else:
        print(f"  ⏭  Exists user: {u['username']}")

    users[u["username"]] = user


# ─────────────────────────────────────────────
# 2. ROOMS (WITH IMAGES)
# ─────────────────────────────────────────────
rooms_data = [
    {
        "name": "Salle A101",
        "room_type": "salle_cours",
        "capacity": 40,
        "location": "Bâtiment A - 1er étage",
        "floor": 1,
        "image_url": "https://images.unsplash.com/photo-1580582932707-520aed937b7b?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "name": "Salle TD-B201",
        "room_type": "salle_td",
        "capacity": 20,
        "location": "Bâtiment B - 2e étage",
        "floor": 2,
        "image_url": "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "name": "Labo Réseau",
        "room_type": "labo",
        "capacity": 25,
        "location": "Bâtiment C - 1er étage",
        "floor": 1,
        "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "name": "Salle Info C301",
        "room_type": "salle_info",
        "capacity": 30,
        "location": "Bâtiment C - 3e étage",
        "floor": 3,
        "image_url": "https://images.unsplash.com/photo-1531482615713-2afd69097998?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "name": "Amphi 500",
        "room_type": "amphi",
        "capacity": 200,
        "location": "Bâtiment D - RDC",
        "floor": 0,
        "image_url": "https://images.unsplash.com/photo-1562774053-701939374585?auto=format&fit=crop&w=1200&q=80"
    },
]

rooms = {}

for r in rooms_data:
    room, created = Room.objects.get_or_create(name=r["name"], defaults=r)
    rooms[r["name"]] = room

    print(f"  {'✅ Created' if created else '⏭  Exists'} room: {r['name']}")


# ─────────────────────────────────────────────
# 3. EQUIPMENT (FINAL IMAGES FIXED)
# ─────────────────────────────────────────────
equip_data = [
    {
        "name": "Vidéoprojecteur",
        "quantity": 10,
        "icon": "📽️",
        "description": "Full HD projector for classrooms",
        "photo_url": "https://images.unsplash.com/photo-1527443154391-507e9dc6c5cc?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "name": "PC Portable",
        "quantity": 20,
        "icon": "💻",
        "description": "High-performance laptops for students",
        "photo_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "name": "Tableau Blanc",
        "quantity": 15,
        "icon": "🖊️",
        "description": "Whiteboard for teaching sessions",
        "photo_url": "https://images.unsplash.com/photo-1509062522246-3755977927d7?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "name": "Micro Sans Fil",
        "quantity": 8,
        "icon": "🎤",
        "description": "Wireless microphone system",
        "photo_url": "https://images.unsplash.com/photo-1516280440614-37939bbacd81?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "name": "Caméra Web",
        "quantity": 6,
        "icon": "📷",
        "description": "HD webcam for online classes",
        "photo_url": "https://images.unsplash.com/photo-1527430253228-e93688616381?auto=format&fit=crop&w=1200&q=80"
    },
    {
        "name": "Rallonge Électrique",
        "quantity": 12,
        "icon": "🔌",
        "description": "Power extension cables",
        "photo_url": "https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=1200&q=80"
    },
]

equipment = {}

for e in equip_data:
    eq, created = Equipment.objects.get_or_create(name=e["name"], defaults=e)
    equipment[e["name"]] = eq

    print(f"  {'✅ Created' if created else '⏭  Exists'} equipment: {e['name']}")


# ─────────────────────────────────────────────
# 4. ROOM RESERVATIONS
# ─────────────────────────────────────────────
today = date.today()

room_reservations = [
    (users["prof_rachid"], rooms["Salle A101"], today, time(8, 0), time(10, 0), "Cours Algo L2", "confirmee"),
    (users["prof_rachid"], rooms["Salle Info C301"], today, time(10, 0), time(12, 0), "TP Base de Données", "confirmee"),
    (users["prof_imane"], rooms["Labo Réseau"], today, time(14, 0), time(16, 0), "TP Réseaux", "confirmee"),
]

for user, room, d, start, end, title, status in room_reservations:
    obj, created = RoomReservation.objects.get_or_create(
        user=user,
        room=room,
        date=d,
        heure_debut=start,
        defaults={
            "heure_fin": end,
            "titre": title,
            "status": status,
            "nombre_personnes": 20
        }
    )

    print(f"  {'✅ Created' if created else '⏭  Exists'} room reservation: {title}")


# ─────────────────────────────────────────────
# 5. EQUIPMENT RESERVATIONS
# ─────────────────────────────────────────────
equipment_reservations = [
    (users["prof_rachid"], equipment["Vidéoprojecteur"], 1, today, time(8, 0), time(10, 0), "Cours Algo"),
    (users["prof_imane"], equipment["Micro Sans Fil"], 2, today, time(14, 0), time(16, 0), "TP Réseaux"),
]

for user, eq, qty, d, start, end, title in equipment_reservations:
    obj, created = EquipmentReservation.objects.get_or_create(
        user=user,
        equipment=eq,
        date=d,
        heure_debut=start,
        defaults={
            "heure_fin": end,
            "quantite": qty,
            "titre": title,
            "status": "confirmee"
        }
    )

    print(f"  {'✅ Created' if created else '⏭  Exists'} equipment reservation: {title}")


# ─────────────────────────────────────────────
# DONE
# ─────────────────────────────────────────────
print("\n🎉 Seed completed successfully!")
print("\n🔑 Demo accounts ready to use:")
print("  admin_emsi / Admin1234!")
print("  prof_rachid / Prof1234!")
print("  prof_imane / Prof1234!")
print("  etudiant_ali / Etud1234!")
print("  etudiant_aya / Etud1234!")
print("  etudiant_omar / Etud1234!")