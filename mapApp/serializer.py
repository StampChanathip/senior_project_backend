from rest_framework import serializers
from . models import *


class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = ['waitedTime', 'origin',
                  'destination', 'pickTime', 'dropTime', 'carId']


class CarSerializer(serializers.ModelSerializer):
    passengers = PassengerSerializer(many=True, read_only=True)

    class Meta:
        model = Car
        fields = ['carId', 'node',
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


class ImportSerializer(serializers.Serializer):
    file = serializers.FileField()

    class Meta:
        fields = ['file']
