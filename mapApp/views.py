from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.viewsets import ViewSet
import pandas as pd
import json
from datetime import datetime, timedelta
from django.db.models import Max, Count
from copy import deepcopy
import xlrd
import pytz

from . models import *
from . serializer import *


def read_file(path):
    file = open(path, "r")
    data = file.read()
    file.close()
    return data


def read_json(path):
    return json.loads(read_file(path))


def handle_passenger():
    Route.objects.all().delete()
    Passenger.objects.all().delete()
    carsAll = CarProperties.objects.all()
    for i in range(1, len(carsAll)):
        dt = datetime.now()
        passengers = []
        pickCount = 0
        dropCount = 0
        isNewCar = False

        car = carsAll[i]
        prevCar = carsAll[i - 1]

        if car.carId != prevCar.carId:
            isNewCar = True

        # get previous car passenger
        if (i > 1):
            prevCarPassenger = Passenger.objects.filter(car=prevCar)
            prevPassCount = sum([passenger.amount
                                for passenger in prevCarPassenger])
            if (len(prevCarPassenger) > 0 and prevPassCount <= 6 and not isNewCar):
                for each in prevCarPassenger:
                    passenger = Passenger(car=car, nodeFrom=each.nodeFrom, nodeTo=each.nodeTo,
                                          amount=each.amount, callTime=each.callTime, pickTime=each.pickTime, dropTime=each.dropTime, waitedTime=each.waitedTime)
                    passengers.append(passenger)

        if (car.status == "pick"):
            desiredTime = (dt.combine(dt, car.arrivalTime) -
                           timedelta(minutes=9, seconds=50)).time()

            pickDemand = Demand.objects.filter(nodeFrom=car.nodeFrom, callTime__range=[
                                               desiredTime, car.arrivalTime], amount__range=[0, car.passengerChange]).order_by('-amount')

            for demand in pickDemand:
                # check is there actually a car that drop this demand and get dropTime
                dropCar = CarProperties.objects.filter(nodeFrom=demand.nodeTo, arrivalTime__range=[
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
                    car.nodeFrom == each.nodeTo)
                if (isCarDrop):
                    passengers.remove(each)
            if dropCount != car.passengerChange:
                # Case: Pick and drop at the same node
                desiredTime = (dt.combine(dt, car.departureTime) -
                               timedelta(minutes=10)).time()
                pickDemand = Demand.objects.filter(nodeFrom=car.nodeFrom, callTime__range=[
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


def handle_dashboard(data):
    DashboardData.objects.all().delete()
    dt = datetime(2024, 1, 1, 00, 00, 00)
    df = pd.read_excel(data, sheet_name=0, dtype=str, skiprows=6)
    row_iterator = df.iterrows()
    _, row = next(row_iterator)

    maxWaitedTime = 0
    totalEmptyTripLength = 0
    totalServiceLength = 0
    totalPostTravelTime = timedelta()
    totalStopTime = timedelta()
    carId = "1"

    for idx, nextRow in row_iterator:
        isNewCar = (int(nextRow["Number"]) - int(row["Number"]) == 1)
        if isNewCar or idx == len(df) - 1:
            maxWaitedTime = Passenger.objects.filter(
                car__carId=carId).aggregate(Max("waitedTime"))['waitedTime__max']
            dashboardData = DashboardData(
                carId=carId, totalStopTime=(dt + totalStopTime).time(), totalPostTravelTime=(dt + totalPostTravelTime).time(),
                totalEmptyTripLength=totalEmptyTripLength, totalServiceLength=totalServiceLength, maxWaitedTime=maxWaitedTime
            )
            dashboardData.save()

            carData = CarProperties.objects.filter(carId=carId).values()
            carChargeData = CarProperties.objects.filter(
                carId=carId, status="charging").values()
            lap = 1
            for each in carChargeData:
                chargeLap = ChargeLap(car=dashboardData, lap=str(
                    lap), timeArrival=each['arrivalTime'], timeCharged=each['stopTime'])
                chargeLap.save()
                lap += 1

            for each in carData:
                count = Passenger.objects.filter(car__id=each['id']).aggregate(
                    Count('amount'))['amount__count']
                passenger = PassengerCount(
                    carId=dashboardData, time=each['arrivalTime'], passengerCount=count)
                passenger.save()

            # clear state
            maxWaitedTime = 0
            totalEmptyTripLength = 0
            totalServiceLength = 0
            totalPostTravelTime = timedelta()
            totalStopTime = timedelta()
            carId = nextRow["Number"]

        if idx == len(df) - 1:
            break
        isProfilePoint = row["Is profile point"] == '1'
        if isProfilePoint:
            post_travel_time_str = row["Post travel time"]
            if not pd.isna(row["Post travel time"]):
                post_travel_time_split = post_travel_time_str.split()
                minutes = 0
                seconds = 0
                for part in post_travel_time_split:
                    if 'min' in part:
                        minutes = int(part.replace('min', ''))
                    elif 's' in part:
                        seconds = int(part.replace('s', ''))
                totalPostTravelTime += timedelta(minutes=minutes,
                                                 seconds=seconds)

            stop_time_str = row["Stop time"]
            if not pd.isna(row["Stop time"]):
                stop_time_split = stop_time_str.split()
                minutes = 0
                seconds = 0
                for part in stop_time_split:
                    if 'min' in part:
                        minutes = int(part.replace('min', ''))
                    elif 's' in part:
                        seconds = int(part.replace('s', ''))
                totalStopTime += timedelta(minutes=minutes,
                                           seconds=seconds)

        if not pd.isna(row["EMPTYTRIPLENGTH"]):
            totalEmptyTripLength += float(row["EMPTYTRIPLENGTH"])
        if not pd.isna(row["EMPTYTRIPLENGTH"]):
            totalServiceLength += float(row["SERVICELENGTH"])

        row = nextRow


@api_view(['GET', 'POST'])
def car_detail(request):

    if request.method == 'GET':
        car = Car.objects.all().order_by('properties__time')
        car_serializer = CarSerializer(car, many=True)
        return Response(car_serializer.data)

    elif request.method == 'POST':
        Car.objects.all().delete()

        data = request.FILES['excel_file']
        df = pd.read_excel(data, sheet_name=0, dtype=str, skiprows=6)
        dt = datetime(2024, 1, 1, 00, 00, 00)
        carProps = []
        routeProps = []
        distance = 0
        positions = []
        stopTime = dt.time()

        startTime = StationTime.objects.filter(
            carId="1").values()[0]["stationTime"]
        stationDepartTime = timedelta(
            hours=startTime.hour, minutes=startTime.minute, seconds=startTime.second)
        row_iterator = df.iterrows()
        _, row = next(row_iterator)
        lastChargeTime = (dt + stationDepartTime)
        for idx, nextRow in row_iterator:
            # handle car properties
            isNewCar = not (int(nextRow["Index"]) - int(row["Index"]) == 1)
            if isNewCar:
                positions = []
                distance = 0
                startTime = StationTime.objects.filter(
                    carId=nextRow["Number"]).values()[0]["stationTime"]
                stationDepartTime = timedelta(
                    hours=startTime.hour, minutes=startTime.minute, seconds=startTime.second)
                lastChargeTime = (dt + stationDepartTime)

            isProfilePoint = row["Is profile point"] == '1'
            nodeFrom = row["Node number"]
            nodeTo = nextRow["Node number"]

            if isProfilePoint:
                if int(idx) - 1 > 0:
                    passengerChange = int(df.loc[int(
                        idx) - 1, 'Post occupancy']) - int(df.loc[int(idx) - 2, 'Post occupancy'])
                else:
                    passengerChange = 0

                carId = row["Number"]
                vehstatus = row['veh status']

                if len(carProps) > 0:
                    if not (carProps[-1].carId != carId):
                        lastChargeTime = carProps[-1].lastChargeTime
                    else:
                        lastChargeTime = (datetime(
                            2024, 1, 1, 00, 00, 00) + stationDepartTime)
                if not pd.isna(row['Relative arrival time']):
                    time = dt.combine(dt, (datetime.strptime(
                        row['Relative arrival time'], "%H:%M:%S") + stationDepartTime).time(), tzinfo=pytz.UTC)
                    arrivalTime = (datetime.strptime(
                        row['Relative arrival time'], "%H:%M:%S") + stationDepartTime).time()
                else:
                    time = (dt + stationDepartTime)
                    arrivalTime = (dt + stationDepartTime).time()

                if not pd.isna(row['Relative departure time']):
                    departureTime = (datetime.strptime(
                        row['Relative departure time'], "%H:%M:%S") + stationDepartTime).time()

                if not pd.isna(row['EMPTYTRIPLENGTH']):
                    distance += float(row['EMPTYTRIPLENGTH']) + \
                        float(row['SERVICELENGTH'])
                else:
                    distance += float(row['SERVICELENGTH'])

                battery = 100 - ((distance / 120)*100)

                if not pd.isna(row['Stop time']):
                    total_seconds = 0
                    for part in row['Stop time'].split():
                        if 'min' in part:
                            total_seconds += int(part.replace('min', '')) * 60
                        elif 's' in part:
                            total_seconds += int(part.replace('s', ''))
                    stopTime = (dt + timedelta(seconds=total_seconds)).time()

                if not pd.isna(row['Time spent at charging area']):
                    vehstatus = 'charging'
                    lastChargeTime = dt.combine(dt, (datetime.strptime(
                        row['Relative arrival time'], "%H:%M:%S") + stationDepartTime).time(), tzinfo=pytz.UTC)
                    distance = 0
                    battery = 100

                # handle positions
                if not isNewCar:

                    link = Link.objects.get(nodeFrom=nodeFrom, nodeTo=nodeTo)
                    geom = {"type": "LineString", "coordinates": [
                        *link.geom.get('coordinates')]}
                    car = Car(geometry=geom)
                    car.save()

                    carProp = CarProperties(car=car, carId=carId, nodeFrom=nodeFrom, nodeTo=nodeTo, status=vehstatus, battery=battery, time=time,
                                            arrivalTime=arrivalTime, departureTime=departureTime, stopTime=stopTime, lastChargeTime=lastChargeTime,
                                            passengerChange=passengerChange, travelDistance=distance, passedLink=positions)
                    carProp.save()
                    carProps.append(carProp)
                    positions = []
                    for each in geom["coordinates"]:
                        positions.append(each)
            else:
                if not isNewCar:
                    link = Link.objects.get(nodeFrom=nodeFrom, nodeTo=nodeTo)
                    for each in link.geom.get('coordinates'):
                        positions.append(each)

            row = nextRow

        # CarProperties.objects.bulk_create(carProps)
        RouteProperties.objects.bulk_create(routeProps)
        handle_passenger()
        handle_dashboard(data)

        car1 = Car.objects.all().order_by('properties__time')
        car_serializer = CarSerializer(car1, many=True)
        return Response({'message': 'Success', "data": car_serializer.data}, status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
def passenger_detail(request):
    if request.method == 'GET':
        passengers = Passenger.objects.all()
        passengers_serializer = PassengerSerializer(passengers, many=True)
        return Response({'message': 'Success', 'data': passengers_serializer.data}, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        None


@api_view(['GET', 'POST'])
def route_detail(request):
    if request.method == 'GET':
        route = Route.objects.all()
        route_serializer = RouteSerializer(route, many=True)
        return Response({'message': 'Success', "data": route_serializer.data}, status=status.HTTP_201_CREATED)

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
        links = []
        for link in linkData:
            coor = [[each[1], each[0]]
                    for each in link["geometry"]['coordinates']]
            linkCoor = Link(nodeFrom=link["properties"]["FROMNODENO"], nodeTo=link["properties"]["TONODENO"], geom={
                            'type': 'LineString', "coordinates": coor})
            links.append(linkCoor)
            linkCoorReverse = Link(nodeFrom=link["properties"]["TONODENO"], nodeTo=link["properties"]["FROMNODENO"], geom={
                'type': 'LineString', "coordinates": coor[::-1]})
            links.append(linkCoorReverse)
        Link.objects.bulk_create(links)
        link = Link.objects.all()
        link_serializer = LinkSerializer(link, many=True)
        return Response({'message': 'Success', 'data': link_serializer.data}, status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
def dashboard(request):
    if request.method == 'GET':
        dashboard = DashboardData.objects.all()
        dashboard_serializer = DashboardSerializer(dashboard, many=True)
        return Response({'message': 'Success', 'data': dashboard_serializer.data}, status=status.HTTP_201_CREATED)

    elif request.method == 'POST':
        DashboardData.objects.all().delete()
        dt = datetime(2024, 1, 1, 00, 00, 00)
        data = request.FILES['excel_file']
        df = pd.read_excel(data, sheet_name=0, dtype=str, skiprows=6)
        row_iterator = df.iterrows()
        _, row = next(row_iterator)

        maxWaitedTime = 0
        totalEmptyTripLength = 0
        totalServiceLength = 0
        totalPostTravelTime = timedelta()
        totalStopTime = timedelta()
        carId = "1"

        for idx, nextRow in row_iterator:
            isNewCar = (int(nextRow["Number"]) - int(row["Number"]) == 1)
            if isNewCar or idx == len(df) - 1:
                maxWaitedTime = Passenger.objects.filter(
                    car__carId=carId).aggregate(Max("waitedTime"))['waitedTime__max']
                print(totalPostTravelTime)
                dashboardData = DashboardData(
                    carId=carId, totalStopTime=(dt + totalStopTime).time(), totalPostTravelTime=(dt + totalPostTravelTime).time(),
                    totalEmptyTripLength=totalEmptyTripLength, totalServiceLength=totalServiceLength, maxWaitedTime=maxWaitedTime
                )
                dashboardData.save()

                carData = CarProperties.objects.filter(carId=carId).values()
                carChargeData = CarProperties.objects.filter(
                    carId=carId, status="charging").values()
                lap = 1
                for each in carChargeData:
                    chargeLap = ChargeLap(car=dashboardData, lap=str(
                        lap), timeArrival=each['arrivalTime'], timeCharged=each['stopTime'])
                    chargeLap.save()
                    lap += 1

                for each in carData:
                    count = Passenger.objects.filter(car__id=each['id']).aggregate(
                        Count('amount'))['amount__count']
                    passenger = PassengerCount(
                        carId=dashboardData, time=each['arrivalTime'], passengerCount=count)
                    passenger.save()

                # clear state
                maxWaitedTime = 0
                totalEmptyTripLength = 0
                totalServiceLength = 0
                totalPostTravelTime = timedelta()
                totalStopTime = timedelta()
                carId = nextRow["Number"]

            if idx == len(df) - 1:
                break
            isProfilePoint = row["Is profile point"] == '1'
            if isProfilePoint:
                post_travel_time_str = row["Post travel time"]
                if not pd.isna(row["Post travel time"]):
                    post_travel_time_split = post_travel_time_str.split()
                    minutes = 0
                    seconds = 0
                    for part in post_travel_time_split:
                        if 'min' in part:
                            minutes = int(part.replace('min', ''))
                        elif 's' in part:
                            seconds = int(part.replace('s', ''))
                    totalPostTravelTime += timedelta(minutes=minutes,
                                                     seconds=seconds)

                stop_time_str = row["Stop time"]
                if not pd.isna(row["Stop time"]):
                    stop_time_split = stop_time_str.split()
                    minutes = 0
                    seconds = 0
                    for part in stop_time_split:
                        if 'min' in part:
                            minutes = int(part.replace('min', ''))
                        elif 's' in part:
                            seconds = int(part.replace('s', ''))
                    totalStopTime += timedelta(minutes=minutes,
                                               seconds=seconds)

            if not pd.isna(row["EMPTYTRIPLENGTH"]):
                totalEmptyTripLength += float(row["EMPTYTRIPLENGTH"])
            if not pd.isna(row["EMPTYTRIPLENGTH"]):
                totalServiceLength += float(row["SERVICELENGTH"])

            row = nextRow

        dashboard = DashboardData.objects.all()
        dashboard_serializer = DashboardSerializer(dashboard, many=True)
        return Response({'message': 'Success', 'data': dashboard_serializer.data}, status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
def passenger_check(request):
    if request.method == 'GET':
        cars = Passenger.objects.all()
        allDemand = Demand.objects.all().values()
        unserveCount = 0
        list = []
        for demand in allDemand:
            passengers = Passenger.objects.filter(
                callTime=demand["callTime"], nodeFrom=demand["nodeFrom"], nodeTo=demand['nodeTo'], amount=demand['amount'])
            if not passengers:
                print(demand, passengers)
                unserveCount += 1
        car_serializer = PassengerSerializer(cars, many=True)
        return Response({'count': unserveCount, 'data': car_serializer.data}, status=status.HTTP_201_CREATED)
    elif request.method == 'POST':
        return


@api_view(['GET', 'POST'])
def station_time(request):
    if request.method == 'GET':
        return Response()
    elif request.method == 'POST':
        data = request.FILES['excel_file']
        df = pd.read_excel(data, sheet_name=0, dtype=str)
        dt = datetime(2024, 1, 1, 00, 00, 00)
        row_iterator = df.iterrows()
        for _, row in row_iterator:
            departureTime = datetime.strptime(
                row['Departure time'], "%H:%M:%S").time()
            stationTime = StationTime(
                carId=row["Number"], stationTime=departureTime)
            stationTime.save()
        stationTimes = StationTime.objects.all()
        stationTimes_serializer = StationTimeSerializer(
            stationTimes, many=True)
        return Response({'message': 'Success', "data": stationTimes_serializer.data}, status=status.HTTP_201_CREATED)
