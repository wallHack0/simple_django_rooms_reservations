from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib import messages
from django.db.models import Q
from reservation_app.models import Room, RoomReservation
from django.utils import timezone
import datetime


# View for the main page of conference rooms
class ConferenceRooms(View):
    def get(self, request):
        return render(request, 'conference_rooms.html')


# View for adding new room
class AddNewRoom(View):
    def get(self, request):
        return render(request, 'add_new_room.html')

    def post(self, request):
        name = request.POST.get('name')
        room_capacity = request.POST.get('room_capacity')
        projector_available = request.POST.get('projector_available', False)

        # Validation for room name
        if not name:
            messages.error(request, 'Room name is required.')
            return render(request, 'add_new_room.html')

        # Check if room already exists
        if Room.objects.filter(name=name).exists():
            messages.error(request, "Room with that name already exists.")
            return render(request, 'add_new_room.html')

        # Validation for room capacity
        if not room_capacity:
            messages.error(request, 'Room capacity is required.')
            return render(request, 'add_new_room.html')
        try:
            room_capacity = int(room_capacity)
            if room_capacity <= 0:
                raise ValueError('Room capacity must be greater than 0.')
        except ValueError as e:
            messages.error(request, str(e))
            return render(request, 'add_new_room.html')

        # No need for validation for projector as it is optional
        projector_available = projector_available == 'on'  # Transform to bool

        Room.objects.create(
            name=name,
            room_capacity=room_capacity,
            projector_available=projector_available
        )

        messages.success(request, "Room has been added successfully.")
        return redirect('conference_rooms')


# View for listing all rooms
class ListOfAllRooms(View):
    def get(self, request):
        today = timezone.now().date()
        rooms = Room.objects.all()
        rooms_with_status = []

        # Determines if each room is occupied today
        for room in rooms:
            is_occupied = RoomReservation.objects.filter(room=room, date=today).exists()
            rooms_with_status.append({
                'room': room,
                'is_occupied': is_occupied
            })

        # Passes rooms with their occupancy status to the template
        return render(request, 'list_of_all_rooms.html', {'rooms_with_status': rooms_with_status})


# View for deleting a room
class RoomDelete(View):
    def get(self, request, id):
        try:
            room = Room.objects.get(pk=id)
            room.delete()
        except Room.DoesNotExist:
            raise Http404('Room does not exist')

        # Redirects to the list of all rooms after deletion
        return redirect('list_of_all_rooms')


# View for modifying room details
class ModifyRoom(View):
    def get(self, request, id):
        room = get_object_or_404(Room, pk=id)

        # Renders the modification form pre-filled with room details
        return render(request, 'modify_room.html', {
            'room': room,
            'projector_available': "yes" if room.projector_available else "no"
        })

    def post(self, request, id):
        # Handles form submission for modifying room details
        # [Similar validation and update logic as in AddNewRoom view]
        room = get_object_or_404(Room, pk=id)
        name = request.POST.get('name')
        room_capacity = request.POST.get('room_capacity')
        projector_available = request.POST.get('projector_available') == 'on'

        if not name:
            messages.error(request, 'Room name is required.')
            return redirect('room_modify', id=id)

        if Room.objects.exclude(pk=id).filter(name=name).exists():
            messages.error(request, "Room with that name already exists.")
            return redirect('room_modify', id=id)

        try:
            room_capacity = int(room_capacity)
            if room_capacity <= 0:
                raise ValueError('Room capacity must be greater than 0.')
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('room_modify', id=id)

        room.name = name
        room.room_capacity = room_capacity
        room.projector_available = projector_available
        room.save()

        messages.success(request, "Room has been modified.")
        return redirect('list_of_all_rooms')


# View for reserving a room
class ReserveRoom(View):
    def get(self, request, id):
        # Renders the reservation form along with existing reservations
        room = get_object_or_404(Room, pk=id)
        reservations = RoomReservation.objects.filter(room=room).order_by('date')
        return render(request, 'reserve_room.html', {'room': room, 'reservations': reservations})

    def post(self, request, id):
        # Validation logic for date and existing reservations
        date = request.POST.get('date')
        comment = request.POST.get('comment')
        room = get_object_or_404(Room, pk=id)
        reservations = RoomReservation.objects.filter(room=room).order_by('date')

        reservation_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()

        if reservation_date < datetime.date.today():
            messages.error(request, 'You cannot reserve a room in the past.')
            return redirect('room_reserve', id=id)

        if RoomReservation.objects.filter(room=room, date=reservation_date).exists():
            messages.error(request, 'This room is already reserved for the selected date.')
            return redirect('room_reserve', id=id)

        RoomReservation.objects.create(
            room=room,
            date=reservation_date,
            comment=comment
        )

        messages.success(request, 'Room has been successfully reserved.')
        return redirect('list_of_all_rooms')


# View for displaying room details including future reservations
class RoomDetails(View):
    def get(self, request, id):
        room = get_object_or_404(Room, pk=id)
        reservations = room.reservations.filter(date__gte=timezone.now().date()).order_by('date')

        return render(request, 'room_details.html', {'room': room, 'reservations': reservations})


# View for deleting reservation
class DeleteReservation(View):
    def get(self, request, reservation_id):
        try:
            reservation = RoomReservation.objects.get(pk=reservation_id)
            room_id = reservation.room.id  # Save room id before removing reservation
            reservation.delete()
            return redirect('room_detail', id=room_id)
        except RoomReservation.DoesNotExist:
            raise Http404('Reservation does not exist')


# View for list of all reservations with search through date option
class ListReservations(View):
    def get(self, request):
        date_query = request.GET.get('date')
        if date_query:
            reservations = RoomReservation.objects.filter(date=date_query).order_by('date')
        else:
            reservations = RoomReservation.objects.all().order_by('date')
        return render(request, 'list_of_reservations.html', {'reservations': reservations})


# View for searching rooms
class SearchRooms(View):
    def get(self, request):
        today = timezone.now().date()

        query = Q()  # Initialize an empty Q object for query

        name = request.GET.get('name', '')
        if name:
            query &= Q(name__icontains=name)  # Add case-insensitive containment test to query

        min_capacity = request.GET.get('min_capacity', '')
        if min_capacity:
            query &= Q(room_capacity__gte=min_capacity)  # Filter rooms with capacity >= min_capacity

        projector = request.GET.get('projector', '')
        if projector:
            query &= Q(projector_available=projector == 'on')  # Filter rooms where projector is available if requested

        # Execute query to get filtered rooms and prepare list to hold rooms
        rooms = Room.objects.filter(query)
        rooms_with_status = []

        # For each room, check if it is occupied today and append the result to rooms_with_status
        for room in rooms:
            is_occupied = RoomReservation.objects.filter(room=room, date=today).exists()
            rooms_with_status.append({
                'room': room,
                'is_occupied': is_occupied
            })

        # Render the list of all rooms template with the rooms (and their status) and search parameters
        return render(request, 'list_of_all_rooms.html', {
            'rooms_with_status': rooms_with_status,
            'search_name': name,
            'search_min_capacity': min_capacity,
            'search_projector': projector == 'on'
        })
