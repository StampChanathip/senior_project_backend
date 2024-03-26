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
import xlrd

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

    if request.method == 'GET':
        car = Car.objects.all()
        car_serializer = CarSerializer(car, many=True)
        return Response(car_serializer.data)

    elif request.method == 'POST':
        Car.objects.all().delete()
        # Passenger.objects.all().delete()

        data = request.FILES['excel_file']
        df = pd.read_excel(data, sheet_name=0, dtype=str, skiprows=6)

        cars = []
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
            elif len(cars) > 1:
                arrivalTime = cars[-1].arrivalTime
            else:
                arrivalTime = (datetime(
                    2024, 1, 1, 00, 00, 00) + timedelta(hours=6, minutes=30)).time()

            if not pd.isna(row['Relative departure time']):
                departureTime = (datetime.strptime(
                    row['Relative departure time'], "%H:%M:%S") + timedelta(hours=6, minutes=30)).time()
            elif len(cars) > 1:
                departureTime = cars[-1].departureTime

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

            car = Car(carId=carId, status=vehstatus, battery=battery, arrivalTime=arrivalTime,
                      departureTime=departureTime, passengerChange=passengerChange)

            # handle positions
            if not isNewCar:
                link = Link.objects.get(nodeFrom=nodeFrom, nodeTo=nodeTo)
                car.link = link
                cars.append(car)
            row = nextRow

        Car.objects.bulk_create(cars)

        # car1 = Car.objects.all()
        # car_serializer = CarSerializer(car1, many=True)
        return Response({'message': 'Success'}, status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
def passenger_detail(request):
    if request.method == 'GET':
        return Response()

    elif request.method == 'POST':
        Passenger.objects.all().delete()
        carsAll = Car.objects.all()
        carPassenger = []
        for i in range(1, len(carsAll)):
            dt = datetime.now()
            passengers = []
            pickCount = 0
            dropCount = 0

            car = carsAll[i]
            prevCar = carsAll[i - 1]

            # get previous car passenger
            if (i > 1):
                prevCarPassenger = Passenger.objects.filter(car=prevCar)
                prevPassCount = sum([passenger.amount
                                    for passenger in prevCarPassenger])
                if (len(prevCarPassenger) > 0 and prevPassCount <= 6):
                    for each in prevCarPassenger:
                        passenger = Passenger(car=car, nodeFrom=each.nodeFrom, nodeTo=each.nodeTo,
                                              amount=each.amount, callTime=each.callTime, pickTime=each.pickTime, dropTime=each.dropTime, waitedTime=each.waitedTime)
                        passengers.append(passenger)

            if (car.status == "pick"):
                desiredTime = (dt.combine(dt, car.arrivalTime) -
                               timedelta(minutes=10)).time()
                
                pickDemand = Demand.objects.filter(nodeFrom=car.link.nodeFrom, callTime__range=[
                                                   desiredTime, car.arrivalTime], amount__range=[0, car.passengerChange]).order_by('-amount')

                for demand in pickDemand:
                    # check is there actually a car that drop this demand and get dropTime
                    dropCar = Car.objects.filter(link__nodeFrom=demand.nodeTo, arrivalTime__range=[
                                                 car.arrivalTime, datetime(2024, 1, 1, 21, 30, 00).time()])
                    if dropCar:
                        pickCount += demand.amount
                        if pickCount > car.passengerChange:
                            break

                        waitedTime = (dt.combine(dt, car.arrivalTime) -
                                      dt.combine(dt, demand.callTime)).total_seconds()
                        passenger = Passenger(car=car, nodeFrom=demand.nodeFrom, nodeTo=demand.nodeTo,
                                              amount=demand.amount, callTime=demand.callTime, pickTime=car.arrivalTime, dropTime=dropCar[0].arrivalTime, waitedTime=waitedTime)
                        passengers.append(passenger)

            elif (car.status == "drop"):
                copyPass = passengers.copy()
                for each in copyPass:
                    dropCount -= each.amount
                    isCarDrop = (
                        car.link.nodeFrom == each.nodeTo)
                    if (isCarDrop):
                        passengers.remove(each)
                if dropCount != car.passengerChange:
                    # Case: Pick and drop at the same node
                    desiredTime = (dt.combine(dt, car.departureTime) -
                                   timedelta(minutes=10)).time()
                    pickDemand = Demand.objects.filter(nodeFrom=car.link.nodeFrom, callTime__range=[
                        desiredTime, car.departureTime], amount__range=[0, (car.passengerChange - dropCount)])
                    for demand in pickDemand:
                        pickCount += demand.amount
                        if pickCount > (car.passengerChange - dropCount):
                            break
                        waitedTime = (dt.combine(dt, car.departureTime) -
                                      dt.combine(dt, demand.callTime)).total_seconds()
                        passenger = Passenger(car=car, nodeFrom=demand.nodeFrom, nodeTo=demand.nodeTo,
                                              amount=demand.amount, callTime=demand.callTime, pickTime=car.departureTime, waitedTime=waitedTime)
                        passengers.append(passenger)
            Passenger.objects.bulk_create(passengers)
            carPassenger.append(passengers)

        carsData = CarSerializer(carsAll, many=True)
        return Response({'message': 'Success', 'car': carsData.data}, status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
def route_detail(request):
    if request.method == 'GET':
        return Response()

    elif request.method == 'POST':
        return Response()


@api_view(['GET', 'POST'])
def demand_detail(request):
    demandData = read_json('senior_project/MockData/demandData.json')
    if request.method == 'GET':
        demand = Demand.objects.all()
        demand_serializer = DemandSerializer(demand, many=True)
        return Response({'message': 'Success', 'data': demand_serializer.data}, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        Demand.objects.all().delete()
        for demand in demandData:
            callTime = datetime.strptime(demand['callTime'], "%H:%M:%S")
            newDemand = Demand(
                callTime=callTime, nodeFrom=demand["nodeFrom"], nodeTo=demand["nodeTo"], amount=demand['amount'])
            newDemand.save()
        demands = Demand.objects.all()
        demand_serializer = DemandSerializer(demands, many=True)
        return Response({'message': 'Success', 'data': demand_serializer.data}, status=status.HTTP_201_CREATED)


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
    
@api_view(['GET', 'POST'])
def dashboard(request):
    if request.method == 'GET':
        return Response()

    elif request.method == 'POST':
        dt = datetime.now()
        data = request.FILES['excel_file']
        df = pd.read_excel(data, sheet_name=0, dtype=str, skiprows=6)
        row_iterator = df.iterrows()
        _, row = next(row_iterator)

        arrival_time = timedelta()
        departure_time = timedelta()
        stop_time = timedelta()
        post_travel_time = timedelta()
        charging_time = timedelta()

        for idx, nextRow in row_iterator:
            if not pd.isna(row['Relative arrival time']):
                if arrival_time:
                    arrivalTime = (datetime.strptime(
                        row['Relative arrival time'], "%H:%M:%S") + timedelta(hours=6, minutes=30)).time()
                    # relative_arrival_time = (datetime.strptime(
                    #     row['Relative arrival time'], "%H:%M:%S") + timedelta(hours=6, minutes=30)).time()
                    # arrival_time = (dt.combine(dt, arrival_time) + dt.combine(dt, relative_arrival_time)).time()
                
            # if not pd.isna(row['Relative departure time']):
            #     if departure_time:
            #         relative_departure_time = (datetime.strptime(
            #             row['Relative departure time'], "%H:%M:%S") + timedelta(hours=6, minutes=30)).time()
            #         departure_time = (dt.combine(dt, departure_time) + dt.combine(dt, relative_departure_time)).time()
            
            # if not pd.isna(row['Stop time']):
            #     stop_time_delta = timedelta()
            #     stop_time_str = row['Stop time']
            #     stop_time_split = stop_time_str.split()
            #     minutes = 0
            #     seconds = 0
            #     for part in stop_time_split:
            #         if 'min' in part:
            #             minutes = int(part.replace('min', ''))
            #         elif 's' in part:
            #             seconds = int(part.replace('s', ''))
            #     stop_time_delta = timedelta(minutes=minutes, seconds=seconds)
            #     if stop_time:
            #         stop_time += stop_time_delta
            
            # if not pd.isna(row['Post travel time']):
            #     post_travel_time_delta = timedelta()
            #     post_travel_time_str = row['Post travel time']
            #     post_travel_time_split = post_travel_time_str.split()
            #     minutes = 0
            #     seconds = 0
            #     for part in post_travel_time_split:
            #         if 'min' in part:
            #             minutes = int(part.replace('min', ''))
            #         elif 's' in part:
            #             seconds = int(part.replace('s', ''))
            #     post_travel_time_delta = timedelta(minutes=minutes, seconds=seconds)
            #     if post_travel_time:
            #         post_travel_time += post_travel_time_delta

            # if not pd.isna(row['Time spent at charging area']):
            #     charging_time_delta = timedelta()
            #     charging_time_str = row['Time spent at charging area']
            #     charging_time_split = charging_time_str.split()
            #     minutes = 0
            #     seconds = 0
            #     for part in charging_time_split:
            #         if 'min' in part:
            #             minutes = int(part.replace('min', ''))
            #         elif 's' in part:
            #             seconds = int(part.replace('s', ''))
            #     charging_time_delta = timedelta(minutes=minutes, seconds=seconds)
            #     if charging_time:
            #         charging_time += charging_time_delta
        
            row = nextRow
        dashboardData = DashboardData(totalArrivalTime=arrival_time, totalDepartureTime=departure_time, totalChargingTime=charging_time,
                                      totalPostTravelTime=post_travel_time, totalStopTime=stop_time)
        dashboardData.save()
        # dashboard = DashboardData.objects.all()
        dashboard_serializer = DashboardSerializer(dashboardData)
        return Response({'message': 'Success', 'data': dashboard_serializer.data}, status=status.HTTP_201_CREATED)
                
            