from rest_framework import serializers
from . models import *


class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = ['callTime', 'nodeFrom', 'nodeTo',
                  'amount', 'pickTime', 'dropTime', 'waitedTime']


class PositionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinates
        fields = ['lat', 'lng']


class LinkSerializer(serializers.ModelSerializer):
    coordinates = PositionsSerializer(many=True, read_only=True)
    
    class Meta:
        model = Link
        fields = ['nodeFrom', 'nodeTo', 'coordinates']
        
class CarSerializer(serializers.ModelSerializer):
    passengers = PassengerSerializer(many=True, read_only=True)
    link = LinkSerializer()

    class Meta:
        model = Car
        fields = ['carId','status', 'battery', 'arrivalTime', "departureTime", 'passengerChange', 'passengers', 'link']

class RouteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Route
        fields = ['nodeNo', 'coordinates', 'density', 'timeStamp']
