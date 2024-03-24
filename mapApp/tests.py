from django.test import TestCase

# Create your tests here.
# import xlrd
# # wb = xlrd.open_workbook("D:\Year 4\project\path item for visualization simp.xlsx")
# wb = xlrd.open_workbook("D:\Year 4\project\Demo.xlsx")
# ws = wb.sheet_by_index(0)
# # for i in range(ws.nrows):
#     # for j in range(ws.ncols):
#         # print(ws.cell_value(i,j), end = "\t")
#     # print('')

# num_rows = ws.nrows
# print(num_rows)
# vehicle_numbers = set(ws.cell_value(row, 0) for row in range(1, num_rows))
# vehicle_datasets = {}
# for vehicle_numbers in vehicle_numbers :
#     vehicle_data = []
#     for row in range(1, num_rows):
#         if ws.cell_value(row, 0) == vehicle_numbers:
#             vehicle_data.append(ws.row_values(row))
#     vehicle_datasets[vehicle_numbers] = vehicle_data
# print(vehicle_data)


# # for i in range(ws.nrows):

import xlrd
from datetime import datetime, timedelta

# Open the Excel file
workbook = xlrd.open_workbook("D:\\Year 4\\project\\Demo.xlsx")

# Assuming the data is in the second sheet
sheet = workbook.sheet_by_index(1)

# Find the column index for arrival time, departure time, stop time, and post travel time
arrival_time_col_index = None
departure_time_col_index = None
stop_time_col_index = None
post_travel_time_col_index = None
for col_index in range(sheet.ncols):
    if sheet.cell_value(0, col_index) == "Relative arrival time":
        arrival_time_col_index = col_index
    elif sheet.cell_value(0, col_index) == "Relative departure time":
        departure_time_col_index = col_index
    elif sheet.cell_value(0, col_index) == "Stop time":
        stop_time_col_index = col_index
    elif sheet.cell_value(0, col_index) == "Post travel time":
        post_travel_time_col_index = col_index

# Dictionary to store time data by vehicle number
time_by_number = {}

# Loop through each row in the Excel file
for row_num in range(1, sheet.nrows):  # Assuming the first row is headers
    # Get vehicle number from column B
    number = sheet.cell_value(row_num, 1)
    if number == '':
        continue  # Skip rows with empty vehicle numbers

    number = int(number)

    # Get arrival and departure time strings
    arrival_time_str = str(sheet.cell_value(row_num, arrival_time_col_index))
    departure_time_str = str(sheet.cell_value(row_num, departure_time_col_index))

    # Convert arrival and departure time strings to datetime.time objects
    if arrival_time_str:
        arrival_time_seconds = round(float(arrival_time_str) * 86400)  # Convert days to seconds
        arrival_time = (datetime.min + timedelta(seconds=arrival_time_seconds)).time()
    else:
        arrival_time = datetime.min.time()

    if departure_time_str:
        departure_time_seconds = round(float(departure_time_str) * 86400)  # Convert days to seconds
        departure_time = (datetime.min + timedelta(seconds=departure_time_seconds)).time()
    else:
        departure_time = datetime.min.time()

    # Update time data for the vehicle number
    if number not in time_by_number:
        time_by_number[number] = {
            'Relative arrival time': timedelta(),
            'Relative departure time': timedelta(),
            'Stop time': timedelta(),
            'Post travel time': timedelta()
        }
    # time_by_number[number]['Relative arrival time'] += timedelta(hours=arrival_time.hour, minutes=arrival_time.minute, seconds=arrival_time.second)
    # time_by_number[number]['Relative departure time'] += timedelta(hours=departure_time.hour, minutes=departure_time.minute, seconds=departure_time.second)
#update : 92-103
# Calculate relative arrival and departure times for each vehicle
    # if 'first_arrival_time' not in time_by_number[number]:
    #     time_by_number[number]['first_arrival_time'] = arrival_time
    # time_by_number[number]['Relative arrival time'] = arrival_time - time_by_number[number]['first_arrival_time']

    # if 'first_departure_time' not in time_by_number[number]:
    #     time_by_number[number]['first_departure_time'] = departure_time
    # time_by_number[number]['Relative departure time'] = departure_time - time_by_number[number]['first_departure_time']

    # # Get stop time and post travel time strings (same as before)
    # stop_time_str = str(sheet.cell_value(row_num, stop_time_col_index))
    # post_travel_time_str = str(sheet.cell_value(row_num, post_travel_time_col_index))
    

# Loop through each row in the Excel file
for row_num in range(1, sheet.nrows):  # Assuming the first row is headers
    # Get vehicle number from column B
    number = sheet.cell_value(row_num, 1)
    if number == '':
        continue  # Skip rows with empty vehicle numbers

    number = int(number)

    # Get arrival and departure time strings
    arrival_time_str = str(sheet.cell_value(row_num, arrival_time_col_index))
    departure_time_str = str(sheet.cell_value(row_num, departure_time_col_index))

    # Convert arrival and departure time strings to datetime.time objects
    if arrival_time_str:
        arrival_time_seconds = round(float(arrival_time_str) * 86400)  # Convert days to seconds
        arrival_time = (datetime.min + timedelta(seconds=arrival_time_seconds)).time()
    else:
        arrival_time = datetime.min.time()

    if departure_time_str:
        departure_time_seconds = round(float(departure_time_str) * 86400)  # Convert days to seconds
        departure_time = (datetime.min + timedelta(seconds=departure_time_seconds)).time()
    else:
        departure_time = datetime.min.time()

    # Get stop time and post travel time strings
    stop_time_str = str(sheet.cell_value(row_num, stop_time_col_index))
    post_travel_time_str = str(sheet.cell_value(row_num, post_travel_time_col_index))

    # Convert stop time and post travel time strings to timedelta objects
    stop_time_delta = timedelta()
    if stop_time_str:
        stop_time_split = stop_time_str.split()
        minutes = 0
        seconds = 0
        for part in stop_time_split:
            if 'min' in part:
                minutes = int(part.replace('min', ''))
            elif 's' in part:
                seconds = int(part.replace('s', ''))
        stop_time_delta = timedelta(minutes=minutes, seconds=seconds)

    post_travel_time_delta = timedelta()
    if post_travel_time_str:
        post_travel_time_split = post_travel_time_str.split()
        minutes = 0
        seconds = 0
        for part in post_travel_time_split:
            if 'min' in part:
                minutes = int(part.replace('min', ''))
            elif 's' in part:
                seconds = int(part.replace('s', ''))
        post_travel_time_delta = timedelta(minutes=minutes, seconds=seconds)

    # Update time data for the vehicle number
    if number not in time_by_number:
        time_by_number[number] = {
            'Relative arrival time': timedelta(),
            'Relative departure time': timedelta(),
            'Stop time': timedelta(),
            'Post travel time': timedelta()
        }
    time_by_number[number]['Relative arrival time'] += timedelta(hours=arrival_time.hour, minutes=arrival_time.minute, seconds=arrival_time.second)
    time_by_number[number]['Relative departure time'] += timedelta(hours=departure_time.hour, minutes=departure_time.minute, seconds=departure_time.second)
    time_by_number[number]['Stop time'] += stop_time_delta
    time_by_number[number]['Post travel time'] += post_travel_time_delta


# Output the results
for number, times in time_by_number.items():
    print(f"Vehicle {number}:")
    print(f"Total Relative Arrival Time: {times['Relative arrival time']}")
    print(f"Total Relative Departure Time: {times['Relative departure time']}")
    print(f"Total Stop Time: {times['Stop time']}")
    print(f"Total Post Travel Time: {times['Post travel time']}")
    print()
