from datetime import datetime
from django.db import models


class Car(models.Model):
    timeStamp = models.TimeField(default=datetime.now, blank=True)
    carId = models.CharField(max_length=20, default="1")
    node = models.CharField(max_length=20, default="0")
    status = models.CharField(max_length=20, default="0")
    battery = models.IntegerField(default=100)


class Passenger(models.Model):
    waitedTime = models.IntegerField(default=0)
    origin = models.CharField(max_length=20, default="0")
    destination = models.CharField(max_length=20, default="0")
    pickTime = models.TimeField(default=datetime.now, blank=True)
    dropTime = models.TimeField(default=datetime.now, blank=True)
    carId = models.ForeignKey(
        Car, related_name='passengers', on_delete=models.CASCADE)


class Route(models.Model):
    timeStamp = models.TimeField(default=datetime.now, blank=True)
    nodeNo = models.CharField(max_length=20, default="0")
    density = models.IntegerField(default=0)


class Coordinates(models.Model):
    routeId = models.ForeignKey(
        Route, related_name='coordinates', on_delete=models.CASCADE)
    lattitude = models.IntegerField(default=0)
    longitude = models.IntegerField(default=0)
