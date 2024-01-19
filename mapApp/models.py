from datetime import datetime
from django.db import models


class Car(models.Model):
    timeStamp = models.DateTimeField(default=datetime.now, blank=True)
    carId = models.CharField(max_length=20, default="1")
    node = models.CharField(max_length=20, default="0")
    status = models.CharField(max_length=20, default="0")
    battery = models.CharField(max_length=20, default="0")


class Passenger(models.Model):
    waitedTime = models.IntegerField(default=0)
    origin = models.CharField(max_length=20, default="0")
    destination = models.CharField(max_length=20, default="0")
    pickTime = models.DateTimeField(default=datetime.now, blank=True)
    dropTime = models.DateTimeField(default=datetime.now, blank=True)
    carId = models.ForeignKey(
        Car, related_name='passengers', on_delete=models.CASCADE)


class Route(models.Model):
    nodeNo = models.CharField(max_length=20, default="0")
    coordinates = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default="0")
    density = models.IntegerField(default=0)
