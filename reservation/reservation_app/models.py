from django.db import models
from django.utils import timezone


# Model representing a conference room
class Room(models.Model):
    name = models.CharField(max_length=255, unique=True)
    room_capacity = models.PositiveIntegerField()
    projector_available = models.BooleanField(default=False)


# Model for reserving a room
class RoomReservation(models.Model):
    date = models.DateField(default=timezone.now)  # The date when the room is reserved
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='reservations')  # The room being reserved
    comment = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('date', 'room',)  # Ensures that a room can be reserved only once per date
        verbose_name = 'Room Reservation'
        verbose_name_plural = 'Room Reservations'
