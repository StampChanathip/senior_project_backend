from datetime import datetime
from django.db import models


class Car(models.Model):
    timeStamp = models.TimeField(default=datetime.now, blank=True)
    carId = models.CharField(max_length=20, default="1")
    nodeFrom = models.CharField(max_length=20, default="0")
    nodeTo = models.CharField(max_length=20, default="0")
    status = models.CharField(max_length=200, default="0")
    battery = models.IntegerField(default=100)


class Coordinates(models.Model):
    car = models.ForeignKey(
        Car, related_name='positions', on_delete=models.CASCADE)
    lat = models.DecimalField(default=0, max_digits=20, decimal_places=14)
    lng = models.DecimalField(default=0, max_digits=20, decimal_places=14)


class Passenger(models.Model):
    callTime = models.TimeField(default=datetime.now, blank=True)
    pickTime = models.TimeField(default=datetime.now, blank=True)
    dropTime = models.TimeField(default=datetime.now, blank=True)
    nodeTo = models.CharField(max_length=20, default="0")
    nodeFrom = models.CharField(max_length=20, default="0")
    waitedTime = models.IntegerField(default=0)
    amount = models.IntegerField(default=0)
    carId = models.ForeignKey(
        Car, related_name='passengers', on_delete=models.CASCADE, default=1)


class Route(models.Model):
    timeStamp = models.TimeField(default=datetime.now, blank=True)
    nodeNo = models.CharField(max_length=20, default="0")
    density = models.IntegerField(default=0)
