from rest_framework import serializers
from . models import *


class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = ['id', 'waitedTime', 'origin',
                  'destination', 'pickTime', 'dropTime', 'carId']


class CarSerializer(serializers.ModelSerializer):
    passengers = PassengerSerializer(many=True, read_only=True)

    class Meta:
        model = Car
        fields = ['timeStamp', 'carId', 'node',
                  'status', 'battery', 'passengers']


class CoordinatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinates
        fields = ['lattitude', 'longitude']


class RouteSerializer(serializers.ModelSerializer):
    coordinates = CoordinatesSerializer(many=True, read_only=True)

    class Meta:
        model = Route
        fields = ['nodeNo', 'coordinates', 'density', 'timeStamp']
