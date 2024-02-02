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
        Car.objects.all().delete()

        data = request.FILES['excel_file']
        df = pd.read_excel(data, sheet_name=0, dtype=str)

        cars = []
        positions = []
        distance = 0

        row_iterator = df.iterrows()
        _, row = next(row_iterator)

        for idx, nextRow in row_iterator:
            # handle car details
            isNewCar = not (int(nextRow["Index"]) - int(row["Index"]) == 1)
            if isNewCar:
                distance = 0

            nodeFrom = row["Node number"]
            nodeTo = nextRow["Node number"]
            carId = row["Number"]
            vehstatus = row['veh status']
            if not pd.isna(row['EMPTYTRIPLENGTH']):
                distance += float(row['EMPTYTRIPLENGTH']) + \
                    float(row['SERVICELENGTH'])
            else:
                distance += float(row['SERVICELENGTH'])
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

            # handle positions
            result = next(
                (obj for obj in linkData
                 if (obj['nodeFrom'] == float(nodeFrom)
                     and obj['nodeTo'] == float(nodeTo))), "0")
            resultReverse = next(
                (obj for obj in linkData
                 if (obj['nodeFrom'] == float(nodeTo)
                     and obj['nodeTo'] == float(nodeFrom))), "0")
            lastFrom = next(
                (obj for obj in linkData
                 if (obj['nodeFrom'] == float(nodeFrom))), "0")
            lastTo = next(
                (obj for obj in linkData
                 if (obj['nodeTo'] == float(nodeFrom))), "0")

            if (result != "0" and not isNewCar):
                for pos in result["coordinates"][:-1]:
                    position = Coordinates(
                        lat=pos[1], lng=pos[0])
                    position.car = car
                    positions.append(position)
                if (idx == df.index[-1]):
                    pos = result["coordinates"][-1]
                    position = Coordinates(
                        lat=pos[1], lng=pos[0])
                    position.car = car
                    positions.append(position)
            elif (resultReverse != "0" and not isNewCar):
                for pos in resultReverse["coordinates"][::-1][:-1]:
                    position = Coordinates(
                        lat=pos[1], lng=pos[0])
                    position.car = car
                    positions.append(position)
                if (idx == df.index[-1]):
                    pos = result["coordinates"][-1]
                    position = Coordinates(
                        lat=pos[1], lng=pos[0])
                    position.car = car
                    positions.append(position)
            elif (isNewCar):
                if (lastFrom != '0'):
                    position = Coordinates(
                        lat=lastFrom["coordinates"][0][1], lng=lastFrom["coordinates"][0][0])
                    position.car = car
                    positions.append(position)
                elif (lastTo != '0'):
                    position = Coordinates(
                        lat=lastTo["coordinates"][-1][1], lng=lastTo["coordinates"][-1][0])
                    position.car = car
                    positions.append(position)
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
