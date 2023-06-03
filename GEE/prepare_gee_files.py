import pandas as pd
import numpy as np
import os

# Read the Excel file
excel_file_path = '/Users/alonhrl/Documents/Alon/MA-MSC/development/GEE/GEE_radiation-04-22.xlsx'
df = pd.read_excel(excel_file_path)

# Convert the 'date and time' column to datetime format
df['system:index'] = pd.to_datetime(df['system:index'], format='%Y%m%dT%H')

# Extract day and hour from the datetime column
df['day'] = df['system:index'].dt.day
df['hour'] = df['system:index'].dt.hour

# Replace non-finite values and empty values with 0
df['surface_solar_radiation_downwards w/m2'] = df['surface_solar_radiation_downwards w/m2'].replace([np.inf, -np.inf, np.nan], 0).fillna(0)

# Exclude negative values
df = df[df['surface_solar_radiation_downwards w/m2'] >= 0]

# Convert radiation values to integers
df['surface_solar_radiation_downwards w/m2'] = df['surface_solar_radiation_downwards w/m2'].astype(int)

# Create a pivot table to rearrange the data
pivot_table = df.pivot(index='day', columns='hour', values='surface_solar_radiation_downwards w/m2')

# Generate the CSV file
tmp_csv_file_path = '/Users/alonhrl/Documents/Alon/MA-MSC/development/GEE/processed/GEE_radiation-12-21-tmp.csv'
pivot_table.to_csv(tmp_csv_file_path)

print("tmp CSV file created successfully!")

df = pd.read_csv(tmp_csv_file_path)
# Drop the first column (day number)
df = df.iloc[:, 1:]

# Exclude the first row (day hour)
df = df.iloc[1:, :]

# Fill empty cells with zeros
df = df.fillna(0)

csv_file_path = '/Users/alonhrl/Documents/Alon/MA-MSC/development/GEE/processed/GEE_radiation-04-22.csv'
df.to_csv(csv_file_path, index=False)

# Delete the tmp CSV file
os.remove(tmp_csv_file_path)

print("Excel file created successfully!")
