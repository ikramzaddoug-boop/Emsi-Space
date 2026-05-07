from .models import Reservation
from rooms.models import Room

def suggest_alternative(room, date, start_time, end_time):
    suggestions = []
    for i in range(1, 4):
        new_start = (start_time.hour + i) % 24
        new_end = (end_time.hour + i) % 24
        conflicts = Reservation.objects.filter(
            room=room,
            date=date,
            start_time__lt=end_time,
            end_time__gt=start_time
        )
        if not conflicts.exists():
            suggestions.append({
                "start": f"{new_start}:00",
                "end": f"{new_end}:00"
            })
    return suggestions

def proposer_creneaux(room, date, duree):
    # Exemple simple : proposer créneaux libres
    reservations = Reservation.objects.filter(room=room, date=date)
    return [f"{r.end_time.hour}:00 - {(r.end_time.hour + duree) % 24}:00" for r in reservations]

def recommander_salles(equipements):
    return Room.objects.filter(equipments__in=equipements).distinct()

def detecter_conflits(room, date, start, end):
    return Reservation.objects.filter(
        room=room, date=date,
        start_time__lt=end, end_time__gt=start
    ).exists()

def optimiser_utilisation():
    # Placeholder : logique d’optimisation globale
    return "Optimisation en cours..."
