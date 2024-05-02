import xlrd
from datetime import datetime, timedelta

# Open the Excel file
workbook = xlrd.open_workbook("C:\\Users\\USER\\Documents\\Civil\\Senior Project\\Data\\mock_all_full.xlsx")

# Assuming the data is in the second sheet
sheet = workbook.sheet_by_index(1)

# Find the column index for arrival time, departure time, stop time, post travel time, empty trip length, and passenger kilometers
arrival_time_col_index = None
departure_time_col_index = None
stop_time_col_index = None
post_travel_time_col_index = None
empty_trip_length_col_index = None
passenger_kilometers_col_index = None

for col_index in range(sheet.ncols):
    header = sheet.cell_value(0, col_index)
    if header == "Relative arrival time":
        arrival_time_col_index = col_index
    elif header == "Relative departure time":
        departure_time_col_index = col_index
    elif header == "Stop time":
        stop_time_col_index = col_index
    elif header == "Post travel time":
        post_travel_time_col_index = col_index
    elif header == "EMPTYTRIPLENGTH":
        empty_trip_length_col_index = col_index
    elif header == "PASSENGER_KILOMETERS":
        passenger_kilometers_col_index = col_index

# Dictionary to store time data by vehicle number
time_by_number = {}

# Dictionary to store length data by vehicle number
length_by_number = {
    'Total empty trip length': {},
    'Total service length': {}
}

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

 # Get empty trip length and passenger kilometers
    empty_trip_length_str = sheet.cell_value(row_num, empty_trip_length_col_index)
    passenger_kilometers_str = sheet.cell_value(row_num, passenger_kilometers_col_index)

# Convert empty trip length and passenger kilometers to floats
    empty_trip_length = float(empty_trip_length_str) if empty_trip_length_str else 0.0
    passenger_kilometers = float(passenger_kilometers_str) if passenger_kilometers_str else 0.0

# Update length data for the vehicle number
    if number not in length_by_number['Total empty trip length']:
        length_by_number['Total empty trip length'][number] = 0.0
    length_by_number['Total empty trip length'][number] += empty_trip_length

    if number not in length_by_number['Total service length']:
        length_by_number['Total service length'][number] = 0.0
    length_by_number['Total service length'][number] += passenger_kilometers


# Output the results
for number, times in time_by_number.items():
    print(f"Vehicle {number}:")
    print(f"Total Relative Arrival Time: {times['Relative arrival time']}")
    print(f"Total Relative Departure Time: {times['Relative departure time']}")
    print(f"Total Stop Time: {times['Stop time']}")
    print(f"Total Post Travel Time: {times['Post travel time']}")
    if number in length_by_number['Total empty trip length']:
        print(f"Total Empty Trip Length: {length_by_number['Total empty trip length'][number]}")
    if number in length_by_number['Total service length']:
        print(f"Total Service Length: {length_by_number['Total service length'][number]}")
    print()

#DONE<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<