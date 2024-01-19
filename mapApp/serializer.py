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
