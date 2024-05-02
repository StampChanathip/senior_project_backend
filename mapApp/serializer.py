from rest_framework import serializers
from . models import *


class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = ['nodeFrom', 'nodeTo',
                  'amount', 'callTime', 'pickTime', 'dropTime', 'waitedTime']


class PositionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinates
        fields = ['lat', 'lng']


class LinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Link
        fields = ['nodeFrom', 'nodeTo', 'geom']


class CarPropertiesSerializer(serializers.ModelSerializer):
    passengers = PassengerSerializer(many=True, read_only=True)

    class Meta:
        model = CarProperties
        fields = ['carId', 'nodeFrom', 'status', 'battery', 'time',
                  'arrivalTime', 'departureTime', 'lastChargeTime', 'passengerChange', 'passengers', 'passedLink']


class CarSerializer(serializers.ModelSerializer):
    properties = CarPropertiesSerializer(read_only=True)

    class Meta:
        model = Car
        fields = ["type", "properties", 'geometry']


class RoutePropertiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteProperties
        fields = ['time', 'nodeNo']


class RouteSerializer(serializers.ModelSerializer):
    properties = RoutePropertiesSerializer(read_only=True)

    class Meta:
        model = Route
        fields = ["type", "properties", 'geometry']


class DemandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Demand
        fields = ['callTime', 'nodeFrom', 'nodeTo', 'amount']


class ChargeLapSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChargeLap
        fields = "__all__"


class PassengerCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = PassengerCount
        fields = ["time", "passengerCount"]


class DashboardSerializer(serializers.ModelSerializer):
    chargeLap = ChargeLapSerializer(many=True, read_only=True)
    passengerData = PassengerCountSerializer(many=True, read_only=True)

    class Meta:
        model = DashboardData
        fields = ['carId', 'totalPostTravelTime', 'totalStopTime',
                  'totalEmptyTripLength', 'totalServiceLength', "maxWaitedTime", 'chargeLap', 'passengerData']
