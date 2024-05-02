import xlrd
from collections import defaultdict

# File path
file_path = r"D:\Year 4\project\path item for visualization simp.xlsx"

# Open the workbook
workbook = xlrd.open_workbook(file_path)

# Choose the second sheet
sheet = workbook.sheet_by_index(1)

# Initialize a dictionary to store charging data for each vehicle
charging_data = defaultdict(list)

# Get the index of each required column
header_row = sheet.row_values(0)
number_index = header_row.index("Number")
charging_index = header_row.index("chargings")
empty_trip_length_index = header_row.index("EMPTYTRIPLENGTH")

# Iterate over rows starting from the second row
for row_index in range(1, sheet.nrows):
    number = sheet.cell_value(row_index, number_index)
    charging_status = sheet.cell_value(row_index, charging_index)
    empty_trip_length = sheet.cell_value(row_index, empty_trip_length_index)

    # Check if the vehicle is charging
    if charging_status == "charging":
        # Initialize the total empty trip length to the current row's value
        total_empty_trip_length = float(empty_trip_length) if empty_trip_length else 0.0

        # Sum the empty trip lengths above and below the current row
        i = row_index - 1
        while i >= 0 and sheet.cell_value(i, charging_index) == "charging":
            if sheet.cell_value(i, empty_trip_length_index):  # Check if cell value is not empty
                total_empty_trip_length += float(sheet.cell_value(i, empty_trip_length_index))
            i -= 1

        i = row_index + 1
        while i < sheet.nrows and sheet.cell_value(i, charging_index) == "charging":
            if sheet.cell_value(i, empty_trip_length_index):  # Check if cell value is not empty
                total_empty_trip_length += float(sheet.cell_value(i, empty_trip_length_index))
            i += 1

        # Add charging data to the dictionary
        charging_data[number].append(total_empty_trip_length)

# Print the charging data in the specified format
print("Charging data:")
for vehicle_number, empty_trip_lengths in charging_data.items():
    print(f" - Vehicle number: {int(vehicle_number)}")
    for lap_num, empty_trip_length in enumerate(empty_trip_lengths, 1):
        print(f"   > Charging lap: {lap_num}")
        print(f"    > Empty trip length for charging: {empty_trip_length}")
