from datetime import datetime
from django.db import models
from djgeojson.fields import PointField, MultiPointField, LineStringField


class Link(models.Model):
    nodeFrom = models.CharField(max_length=20, default="0")
    nodeTo = models.CharField(max_length=20, default="0")
    geom = LineStringField()

class Coordinates(models.Model):
    link = models.ForeignKey(
        Link, related_name="coordinates", on_delete=models.CASCADE)
    lat = models.DecimalField(default=0, max_digits=20, decimal_places=14)
    lng = models.DecimalField(default=0, max_digits=20, decimal_places=14)

class Car(models.Model):
    type = models.CharField(max_length=20, default="Feature")
    geometry = LineStringField()

class CarProperties(models.Model):
    car =  models.OneToOneField(
        Car, related_name="properties", on_delete=models.CASCADE)
    carId = models.CharField(max_length=20, default="1")
    nodeFrom = models.CharField(max_length=20, default="0")
    nodeTo = models.CharField(max_length=20, default="0")
    time = models.DateTimeField(default=datetime.now, blank=True)
    arrivalTime = models.TimeField(default=datetime.now, blank=True)
    departureTime = models.TimeField(default=datetime.now, blank=True)
    lastChargeTime = models.DateTimeField(default=datetime.now, blank=True)
    status = models.CharField(max_length=200, default="0")
    battery = models.IntegerField(default=100)
    passengerChange = models.IntegerField(default=0)
    passedLink = LineStringField()


class Passenger(models.Model):
    car = models.ForeignKey(
        CarProperties, related_name='passengers', on_delete=models.CASCADE, default=1)
    callTime = models.TimeField(default=datetime.now, blank=True)
    pickTime = models.TimeField(default=datetime.now, blank=True)
    dropTime = models.TimeField(default=datetime.now, blank=True)
    nodeTo = models.CharField(max_length=20, default="0")
    nodeFrom = models.CharField(max_length=20, default="0")
    waitedTime = models.IntegerField(default=0)
    amount = models.IntegerField(default=0)

class Demand(models.Model):
    callTime = models.TimeField(default=datetime.now, blank=True)
    nodeTo = models.CharField(max_length=20, default="0")
    nodeFrom = models.CharField(max_length=20, default="0")
    amount = models.IntegerField(default=0)

class Route(models.Model):
    type = models.CharField(max_length=20, default="Feature")
    geometry = LineStringField()
    
class RouteProperties(models.Model):
    route = models.OneToOneField(
        Route, related_name="properties", on_delete=models.CASCADE)
    time = models.TimeField(default=datetime.now, blank=True)
    nodeNo = models.CharField(max_length=20, default="0")

class DashboardData(models.Model):
    carId = models.CharField(max_length=20, default="1")
    maxWaitedTime = models.IntegerField(default=0)
    totalEmptyTripLength = models.FloatField(default=0) #in meter
    totalServiceLength = models.FloatField(default=0) #in meter
    totalPostTravelTime = models.TimeField(default=datetime.now, blank=True)
    totalStopTime = models.TimeField(default=datetime.now, blank=True)

class PassengerCount(models.Model):
    carId = models.ForeignKey(
        DashboardData, related_name='passengerData', on_delete=models.CASCADE, default=1)
    time = models.TimeField(default=datetime.now, blank=True)
    passengerCount = models.IntegerField(default=0)
    
class ChargeLap(models.Model):
    car = models.ForeignKey(
        DashboardData, related_name='chargeLap', on_delete=models.CASCADE, default=1)
    lap = models.CharField(max_length=20, default="1")
    timeArrival = models.TimeField(default=datetime.now, blank=True)
    timeCharged = models.TimeField(default=datetime.now, blank=True)