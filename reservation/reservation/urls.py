"""
URL configuration for reservation project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from reservation_app.views import ConferenceRooms, AddNewRoom, ListOfAllRooms, RoomDelete, ModifyRoom, ReserveRoom, RoomDetails, ListReservations, DeleteReservation, SearchRooms

urlpatterns = [
    path('admin/', admin.site.urls),

    path('conference_rooms/', ConferenceRooms.as_view(), name='conference_rooms'),
    path('conference_rooms/add_new_room/', AddNewRoom.as_view(), name='add_new_room'),
    path('conference_rooms/list_of_all_rooms/', ListOfAllRooms.as_view(), name='list_of_all_rooms'),
    path('room/delete/<int:id>/', RoomDelete.as_view(), name='room_delete'),
    path('room/modify/<int:id>/', ModifyRoom.as_view(), name='room_modify'),
    path('room/reserve/<int:id>/', ReserveRoom.as_view(), name='room_reserve'),
    path('room/detail/<int:id>/', RoomDetails.as_view(), name='room_detail'),
    path('conference_rooms/list_of_reservations', ListReservations.as_view(), name='list_of_reservations'),
    path('delete-reservation/<int:reservation_id>/', DeleteReservation.as_view(), name='delete_reservation'),
    path('search_rooms/', SearchRooms.as_view(), name='search_rooms'),
]

