from rest_framework import serializers
from . models import *


class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = ['waitedTime', 'origin',
                  'destination', 'pickTime', 'dropTime', 'carId']


class PositionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinates
        fields = ['lat', 'lng']


class CarSerializer(serializers.ModelSerializer):
    passengers = PassengerSerializer(many=True, read_only=True)
    positions = PositionsSerializer(many=True, read_only=True)

    class Meta:
        model = Car
        fields = ['carId', 'nodeFrom', 'nodeTo',
                  'status', 'battery', 'passengers', 'positions']


class RouteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Route
        fields = ['nodeNo', 'coordinates', 'density', 'timeStamp']
