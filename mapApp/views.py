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
        # try:
        # except Exception:
        #     return Response({'message': 'Fail'}, status=status.HTTP_400_BAD_REQUEST)
            Car.objects.all().delete()
            data = request.FILES['excel_file']
            df = pd.read_excel(data, sheet_name=0, dtype=str)
            cars = []
            distance = 0
            
            for i, row in df.iterrows():
                carId = row['Number']
                node = row['Node number']
                vehstatus = row['veh status']
                distance += float(row['EMPTYTRIPLENGTH']) + float(row['SERVICELENGTH'])
                battery = 100 -((distance / 120)*100)
                if not pd.isna(row['Time spent at charging area']) :
                    vehstatus = 'charging'
                    distance = 0
                    battery = 100 
                car = Car(carId=carId, node=node, status=vehstatus, battery=battery)
                cars.append(car)
            car_serializer = CarSerializer(cars, many=True)
            Car.objects.bulk_create(cars)
            return Response({'message': 'Success', 'data': car_serializer.data}, status=status.HTTP_201_CREATED)


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
