# Generated by Django 5.0.1 on 2024-03-24 04:16

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapApp', '0040_demand_alter_car_link'),
    ]

    operations = [
        migrations.CreateModel(
            name='DashboardData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('totalArrivalTime', models.TimeField(blank=True, default=datetime.datetime.now)),
                ('totalDepartureTime', models.TimeField(blank=True, default=datetime.datetime.now)),
                ('totalStopTime', models.TimeField(blank=True, default=datetime.datetime.now)),
                ('totalPostTravelTime', models.TimeField(blank=True, default=datetime.datetime.now)),
                ('totalChargingTime', models.TimeField(blank=True, default=datetime.datetime.now)),
            ],
        ),
    ]
