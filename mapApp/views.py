from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.viewsets import ViewSet
import pandas as pd
import json
from datetime import datetime, timedelta
from django.db.models import Count
from copy import deepcopy

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
    demandData = read_json('senior_project/MockData/demandData.json')
    
    if request.method == 'GET':
        car = Car.objects.all()
        car_serializer = CarSerializer(car, many=True)
        return Response(car_serializer.data)

    elif request.method == 'POST':
        Car.objects.all().delete()

        data = request.FILES['excel_file']
        df = pd.read_excel(data, sheet_name=0, dtype=str, skiprows=6)

        cars = []
        positions = []
        distance = 0
        carPassenger = []

        row_iterator = df.iterrows()
        _, row = next(row_iterator)

        for idx, nextRow in row_iterator:

            # handle car details
            isNewCar = not (int(nextRow["Index"]) - int(row["Index"]) == 1)
            if isNewCar:
                distance = 0

            nodeFrom = row["Node number"]
            nodeTo = nextRow["Node number"]

            if int(idx) - 1 > 0:
                passengerChange = int(df.loc[int(
                    idx) - 1, 'Post occupancy']) - int(df.loc[int(idx) - 2, 'Post occupancy'])
            else:
                passengerChange = 0

            carId = row["Number"]
            vehstatus = row['veh status']

            if not pd.isna(row['Relative arrival time']):
                arrivalTime = (datetime.strptime(
                    row['Relative arrival time'], "%H:%M:%S") + timedelta(hours=6, minutes=30)).time()
            else:
                arrivalTime = (datetime(
                    2024, 1, 1, 00, 00, 00) + timedelta(hours=6, minutes=30)).time()

            if not pd.isna(row['Relative departure time']):
                departureTime = (datetime.strptime(
                    row['Relative departure time'], "%H:%M:%S") + timedelta(hours=6, minutes=30)).time()

            if not pd.isna(row['EMPTYTRIPLENGTH']):
                distance += float(row['EMPTYTRIPLENGTH']) + \
                    float(row['SERVICELENGTH'])
            else:
                distance += float(row['SERVICELENGTH'])
            battery = 100 - ((distance / 120)*100)

            if not pd.isna(row['Time spent at charging area']):
                vehstatus = 'charging'
                distance = 0
                battery = 100

            car = Car(carId=carId, status=vehstatus, battery=battery, arrivalTime=arrivalTime, departureTime=departureTime, passengerChange=passengerChange)

            # handle positions
            if not isNewCar:
                link = Link.objects.get(nodeFrom=nodeFrom, nodeTo=nodeTo)
                car.link = link
                cars.append(car)
            row = nextRow
            
            # TODO: handle passenger
            # demandIndex = 0
            # passengers = []
            # if row["Is profile point"] == "1":
            #     # get passengers from previous car
            #     if (len(carPassenger) > 0):
            #         prevCarPassenger = carPassenger[-1]
            #         prevPassCount = sum([passenger.amount
            #                             for passenger in prevCarPassenger])
            #         if (len(prevCarPassenger) > 0 and prevPassCount <= 6):
            #             for each in prevCarPassenger:
            #                 passenger = deepcopy(each)
            #                 passenger.car = car
            #                 passengers.append(passenger)

            #     pickCount = 0
            #     dropCount = 0

            #     # drop passenger
            #     copyPass = passengers.copy()
            #     for each in copyPass:
            #         isCarDrop = (
            #             car.nodeFrom == each.nodeTo and passengerChange >= dropCount)
            #     if (isCarDrop):
            #         dropCount += each.amount
            #         passengers.remove(each)

            #         # pick passenger
            #     for i in range(demandIndex, len(demandData)):
            #         demand = demandData[i]
            #         dt = datetime.now()

            #         callTime = datetime.strptime(
            #             demand['callTime'], "%H:%M:%S")
            #         minWaitedTime = (dt.combine(
            #             dt, arrivalTime) - dt.combine(dt, callTime.time())).total_seconds()
            #         maxWaitedTime = (dt.combine(
            #             dt, departureTime) - dt.combine(dt, callTime.time())).total_seconds()

            #         nodePassFrom = demand["nodeFrom"]
            #         nodePassTo = demand["nodeTo"]
            #         # max wait time = 10 min
            #         isCarPick = (
            #             car.nodeFrom == nodePassFrom and ((minWaitedTime <= 600 and minWaitedTime > 0) or (maxWaitedTime <= 600 and maxWaitedTime > 0)) and passengerChange >= pickCount + demand['amount'])
            #     if (isCarPick):
            #         pickCount += demand['amount']
            #         demandIndex += 1
            #         passenger = Passenger(
            #             nodeFrom=nodePassFrom, nodeTo=nodePassTo, callTime=callTime, amount=demand['amount'], car=car, pickTime=arrivalTime, waitedTime=minWaitedTime)
            #         passengers.append(passenger)

            #     carPassenger.append(passengers)
            # elif row["Is profile point"] == "0":
            #     if (len(carPassenger) > 0):
            #         prevCarPassenger = carPassenger[-1]
            #         prevPassCount = sum([passenger.amount
            #                             for passenger in prevCarPassenger])
            #         if (len(prevCarPassenger) > 0 and prevPassCount <= 6):
            #             for each in prevCarPassenger:
            #                 passenger = deepcopy(each)
            #                 passenger.car = car
            #                 passengers.append(passenger)
            #     vehstatus = "run"
            #     carPassenger.append(passengers)

        Car.objects.bulk_create(cars)
        # for each in carPassenger:
        #     if (len(each) > 0):
        #         Passenger.objects.bulk_create(each)

        car1 = Car.objects.all()
        car_serializer = CarSerializer(car1, many=True)
        return Response({'message': 'Success', 'data': car_serializer.data}, status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
def passenger_detail(request):
    if request.method == 'GET':
        return Response()

    elif request.method == 'POST':
        Passenger.objects.all().delete()
        demandData = read_json('senior_project/MockData/demandData.json')

        cars = []
        dropCars = []
        for demand in demandData:
            dt = datetime.now()

            callTime = datetime.strptime(
                demand['callTime'], "%H:%M:%S")

            desiredTime = callTime + timedelta(minutes=5)
            desiredArriveTime = callTime + timedelta(hours=1)

            nodePassFrom = demand["nodeFrom"]
            nodePassTo = demand["nodeTo"]

            pickCar = Car.objects.filter(nodeFrom=nodePassFrom, arrivalTime__range=[
                callTime, desiredTime], status="pick", passengerChange=demand['amount'])

            for car in pickCar:

                waitedTime = (dt.combine(
                    dt, car.arrivalTime) - dt.combine(dt, callTime.time())).total_seconds()

                passenger = Passenger(
                    nodeFrom=nodePassFrom, nodeTo=nodePassTo, callTime=callTime, amount=demand['amount'], car=car, pickTime=car.arrivalTime, waitedTime=waitedTime)
                passenger.save()

        passengerData = PassengerSerializer(Passenger.objects.all(), many=True)
        carsData = CarSerializer(Car.objects.filter(status="pick"), many=True)
        return Response({'message': 'Success', 'car': carsData.data}, status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
def route_detail(request):
    if request.method == 'GET':
        return Response()

    elif request.method == 'POST':
        return Response()
    
@api_view(['GET', 'POST'])
def link_detail(request):
    linkData = read_json('senior_project/MockData/linkCoor.json')
    if request.method == 'GET':
        return Response()

    elif request.method == 'POST':
        Link.objects.all().delete()
        for link in linkData:
            linkCoor = Link(nodeFrom=link["nodeFrom"], nodeTo=link["nodeTo"])
            linkCoor.save()
            for coor in link['coordinates']:
                coordinate = Coordinates(lat=coor[1], lng=coor[0])
                coordinate.link = linkCoor
                coordinate.save()
        for link in linkData:
            linkCoor = Link(nodeFrom=link["nodeTo"], nodeTo=link["nodeFrom"])
            linkCoor.save()
            coorReverse = link['coordinates'][::-1]
            for coor in coorReverse:
                coordinate = Coordinates(lat=coor[1], lng=coor[0])
                coordinate.link = linkCoor
                coordinate.save()
        link = Link.objects.all()
        link_serializer = LinkSerializer(link, many=True)
        return Response({'message': 'Success', 'data': link_serializer.data}, status=status.HTTP_201_CREATED)
