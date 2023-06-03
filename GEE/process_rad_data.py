import ee
import pandas as pd

# Path to the service account key file
service_account_key_file = '/Users/alonhrl/Documents/Alon/MA-MSC/development/plasma-column-387418-7efbfdf9641f.json'

# Initialize the Earth Engine Python API
ee.Initialize()

# Define the location
bar_ilan = ee.Geometry.Point(34.84, 32.07)

# Define the date range
start_date = '2020-07-01'
end_date = '2020-07-02'

# Load the dataset
dataset = ee.ImageCollection("ECMWF/ERA5_LAND/HOURLY") \
    .select('surface_solar_radiation_downwards') \
    .filter(ee.Filter.date(start_date, end_date))

# Filter the dataset based on the location
ts = dataset.filterBounds(bar_ilan)

# Convert the image collection to a pandas DataFrame
radiation_data = ts.toBands().toShort().reduceRegion(
    reducer=ee.Reducer.toList(),
    geometry=bar_ilan,
    scale=1000  # Adjust the scale as per your requirements
)

# Convert the dictionary of pixel values to a pandas DataFrame
df = pd.DataFrame(radiation_data.getInfo())

# Transpose the DataFrame to have dates as rows and bands (hours) as columns
df = df.transpose()

# Set the column names as the hour of the day
df.columns = [f'Hour_{i}' for i in range(len(df.columns))]

# Save the DataFrame to an Excel file
output_path = 'radiation_data.xlsx'
df.to_excel(output_path, index=True)
print(f"Radiation data saved to {output_path}.")
