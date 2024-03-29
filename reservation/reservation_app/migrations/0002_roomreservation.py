# Generated by Django 5.0.1 on 2024-02-06 12:31

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservation_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoomReservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('comment', models.TextField(blank=True, null=True)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservations', to='reservation_app.room')),
            ],
            options={
                'verbose_name': 'Room Reservation',
                'verbose_name_plural': 'Room Reservations',
                'unique_together': {('date', 'room')},
            },
        ),
    ]
