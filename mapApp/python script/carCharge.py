import xlrd
from datetime import timedelta, datetime

# Function to convert floating-point time to AM/PM format
def convert_to_ampm(float_time):
    base_time = datetime(1899, 12, 30)
    time_delta = timedelta(days=float_time)
    target_time = base_time + time_delta
    return target_time.strftime("%I:%M:%S %p")

# Path to the Excel file
file_path = "D:\\Year 4\\project\\path item for visualization simp.xlsx"

# Open the workbook
workbook = xlrd.open_workbook(file_path)

# Select the second sheet
sheet = workbook.sheet_by_index(1)

# Find the column indices of "Relative arrival time", "chargings", and "Time spent at charging area"
relative_arrival_time_col = None
chargings_col = None
charging_area_time_col = None

for col_index in range(sheet.ncols):
    header = sheet.cell_value(0, col_index)
    if header == "Relative arrival time":
        relative_arrival_time_col = col_index
    elif header == "chargings":
        chargings_col = col_index
    elif header == "Time spent at charging area":
        charging_area_time_col = col_index

if relative_arrival_time_col is None or chargings_col is None or charging_area_time_col is None:
    print("Required columns not found in the Excel file.")
    exit()

# Dictionary to store charging times for each vehicle
charging_times = {}

# Dictionary to store charging times spent for each vehicle
charging_times_spent = {}

# Iterate through rows to collect charging times and charging times spent
for row_index in range(1, sheet.nrows):
    vehicle_number = int(sheet.cell_value(row_index, 1))  # Assuming vehicle number is in column B
    arrival_time = sheet.cell_value(row_index, relative_arrival_time_col)
    charging_status = sheet.cell_value(row_index, chargings_col)
    charging_area_time_str = sheet.cell_value(row_index, charging_area_time_col)

    if vehicle_number not in charging_times:
        charging_times[vehicle_number] = []

    if vehicle_number not in charging_times_spent:
        charging_times_spent[vehicle_number] = []

    if charging_status.lower() == "charging":
        # Convert arrival_time to AM/PM format
        arrival_time_ampm = convert_to_ampm(arrival_time)
        charging_times[vehicle_number].append(arrival_time_ampm)

        # Parse charging_area_time_str to extract minutes and seconds
        parts = charging_area_time_str.split()
        total_seconds = 0
        for part in parts:
            if 'min' in part:
                total_seconds += int(part.replace('min', '')) * 60
            elif 's' in part:
                total_seconds += int(part.replace('s', ''))
        
        # Convert total_seconds to timedelta
        charging_time_spent_delta = timedelta(seconds=total_seconds)
        charging_times_spent[vehicle_number].append(charging_time_spent_delta)

# Print charging information for each vehicle
for vehicle, arrival_times in charging_times.items():
    print(f"Vehicle {vehicle}")
    if arrival_times:
        for i, arrival_time in enumerate(arrival_times, start=1):
            print(f"    > Charging lap : {i}")
            print(f"        > Charging time arrival : {arrival_time}")
            print(f"        > Charging time spent : {charging_times_spent[vehicle][i-1]}")
    else:
        print("    > (▀̿Ĺ̯▀̿ ̿) (▀̿Ĺ̯▀̿ ̿) (▀̿Ĺ̯▀̿ ̿) >> No charge baby << (▀̿Ĺ̯▀̿ ̿) (▀̿Ĺ̯▀̿ ̿) (▀̿Ĺ̯▀̿ ̿)")


#DONE >>> Display charging time spent and time arrival for charging
