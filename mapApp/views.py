from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.viewsets import ViewSet
import pandas as pd
import json

from . models import *
from . serializer import *


def read_file(path):
    file = open(path, "r")
    data = file.read()
    file.close()
    return data


def read_json(path):
    return json.loads(read_file(path))


@api_view(['GET', 'POST'])
def car_detail(request):
    linkData = read_json('senior_project/MockData/linkCoor.json')
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
        positions = []
        distance = 0

        row_iterator = df.iterrows()
        _, row = next(row_iterator)

        for _, nextRow in row_iterator:
            nodeFrom = row["Node number"]
            nodeTo = nextRow["Node number"]
            carId = row["Number"]
            vehstatus = row['veh status']
            distance += float(row['EMPTYTRIPLENGTH']) + \
                float(row['SERVICELENGTH'])
            battery = 100 - ((distance / 120)*100)

            if not pd.isna(row['veh status']):
                vehstatus = row['veh status']
            else:
                vehstatus = "run"

            if not pd.isna(row['Time spent at charging area']):
                vehstatus = 'charging'
                distance = 0
                battery = 100

            car = Car(carId=carId, nodeFrom=nodeFrom, nodeTo=nodeTo,
                      status=vehstatus, battery=battery)
            cars.append(car)

            result = next(
                (obj for obj in linkData
                 if (obj['nodeFrom'] == float(nodeFrom)
                     and obj['nodeTo'] == float(nodeTo))), "0")
            resultReverse = next(
                (obj for obj in linkData
                 if (obj['nodeFrom'] == float(nodeTo)
                     and obj['nodeTo'] == float(nodeFrom))), "0")

            if (result != "0"):
                for pos in result["coordinates"]:
                    position = Coordinates(
                        lat=pos[1], lng=pos[0])
                    position.car = car
                    positions.append(position)
            elif (resultReverse != "0"):
                for pos in resultReverse["coordinates"][::-1]:
                    position = Coordinates(
                        lat=pos[1], lng=pos[0])
                    position.car = car
                    positions.append(position)
#
            row = nextRow

        Car.objects.bulk_create(cars)
        for each in positions:
            each.car_id = each.car.id
        Coordinates.objects.bulk_create(positions)

        car1 = Car.objects.all()
        car_serializer = CarSerializer(car1, many=True)
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
