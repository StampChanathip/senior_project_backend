from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.viewsets import ViewSet
import pandas as pd

from . models import *
from . serializer import *


@api_view(['GET', 'POST'])
def car_detail(request):
    if request.method == 'GET':
        car = Car.objects.all()
        car_serializer = CarSerializer(car, many=True)
        return Response(car_serializer.data)

    elif request.method == 'POST':
        serializer = CarSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def passenger_detail(request):
    if request.method == 'GET':
        return Response()

    elif request.method == 'POST':
        return Response()


@api_view(['GET', 'POST'])
def route_detail(request):
    if request.method == 'GET':
        return Response()

    elif request.method == 'POST':
        return Response()
