import netCDF4 as nc
'''
This code receives an input directory with Eumetsat NetCDF files and longitude and latitude baoundaries.
It creates a CSV file with the following columns:
longitude | latitude | date | daily-radiation
'''


import pandas as pd
import numpy as np
import glob
import os
import csv
from netCDF4 import Dataset

minlat = 29.5
maxlat = 33.25
minlon = 34.38
maxlon = 35.8
count = 0

def get_file_hour_month_year(fileName):
    #extract last part in the file name which is the date
    filename = os.path.basename(fileName)
    tempTuple = os.path.splitext(filename)
    filename = tempTuple[0]
    fileNameArr = np.array(filename.split("-"))
    filedate = fileNameArr[len(fileNameArr)-1]
    
    #the format is 222001010900Z YYYYMMDDHHMM
    year = int(filedate[:4])
    month = int(filedate[4:6])
    day = int(filedate[6:8])
    hour = int(filedate[8:10])
    minute = int(filedate[10:12])
    
    return (year, month, day, hour)

def find_start_lat_lon_and_interval(filename):
    
    nc_file = Dataset(filename)
    
    lat_var = nc_file.variables['lat']
    lats_size = len(lat_var)
    lat_start = lat_var[0] if (lat_var[0] < lat_var[lats_size-1]) else lat_var[lats_size-1]
    
    lon_var = nc_file.variables['lon']
    lons_size = len(lon_var)
    lon_start = lon_var[0] if (lon_var[0] < lon_var[lons_size-1]) else lon_var[lons_size-1]
    
    # we assume lats % lons have the same interval 
    interval = (abs(lat_var[0]) + abs(lat_var[lats_size-1]))/lats_size
                
    return(lon_start, lat_start , round(interval, 2))

def calc_first_and_last_indices_for_range(filename, minlon, maxlon, minlat, maxlat):
    
    #find start lats & lons
    lon_start, lat_start , interval = find_start_lat_lon_and_interval(filename)
    
    #print("lon_start %d, lat_start %d, interval %f" %(lon_start, lat_start , interval))
    #print("minlon %f, maxlon %f, minlat %f, maxlat %f" %(minlon, maxlon, minlat, maxlat))
    latOffsetStart =  (minlat+abs(lat_start))/interval
    latOffsetEnd =  (maxlat+abs(lat_start))/interval
    lonOffsetStart =  (minlon+abs(lon_start))/interval
    lonOffsetEnd =  (maxlon+abs(lon_start))/interval
    
    #get the coordinates values from the file
    nc_file = Dataset(filename)  
    lat_var = nc_file.variables['lat']
    lon_var = nc_file.variables['lon']
    
    #find the cells which are closest to the start & end coordinates for lat and lon
    latStartOffset = latOffsetStart if (((minlat - lat_var[latOffsetStart])) < (lat_var[latOffsetStart+1] - minlat)) else latOffsetStart
    latEndOffset = latOffsetEnd if (((maxlat - lat_var[latOffsetEnd])) < (lat_var[latOffsetEnd+1] - maxlat)) else latOffsetEnd
    lonStartOffset = lonOffsetStart if (((minlon - lon_var[lonOffsetStart])) < (lon_var[lonOffsetStart+1] - minlon)) else lonOffsetStart
    lonEndOffset = lonOffsetEnd if (((maxlon - lon_var[lonOffsetEnd])) < (lon_var[lonOffsetEnd+1] - maxlon)) else lonOffsetEnd
    
    return(round(lonStartOffset), round(lonEndOffset), round(latStartOffset), round(latEndOffset))

inputDir = '/Users/alonhrl/Downloads/Archive'
output_csv_file = os.path.join(inputDir, 'daily_eumetsat_rad.csv')

#we assume same array size for all files thus we choose some file to make the calc and get the fixed data
fileName = file_path = os.path.join(inputDir, 'S-OSI_-FRA_-MSG_-DLISSIH_____-202201010000Z.nc')
minLon, maxLon, minLat, maxLat = calc_first_and_last_indices_for_range(fileName, minlon, maxlon, minlat, maxlat)
lon_start, lat_start , interval = find_start_lat_lon_and_interval(fileName)
# Initialize lon_lat_date_arr as a list of lists with None values
lon_lat_date_arr = [[{} for _ in range(maxLat - minLat + 1)] for _ in range(maxLon - minLon + 1)]



# iterate recursively over all netCDF files in the directory
for filename in glob.iglob(inputDir + '**/**', recursive=True):
    file_name, file_extension = os.path.splitext(filename)
    if file_extension == '.nc':
        count += 1
        
        fh = Dataset(filename, mode='r')
        ssi = fh.variables['ssi']

        # iterate over all indices
        for lonIndex in range(minLon, maxLon + 1):
            for latIndex in range(minLat, maxLat + 1):
                # print("time: %s, lonIndx: %d, latIndx: %d,  ssi: %.2f" %(get_file_date(filename), cLon, cLat, ssi[cLon,cLat]))
                year, month, day, hour = get_file_hour_month_year(filename)
                date = f"{day:02d}-{month:02d}-{year:02d}"
                # if specific date is not in the list -> add it
                #need to subtract the min index values as our array starts from 0
                if not date in lon_lat_date_arr[lonIndex-minLon][latIndex-minLat].keys():
                    lon_lat_date_arr[lonIndex-minLon][latIndex-minLat][date] = 0
                               
                ssiVal = ssi[latIndex, lonIndex]
                # if value is 'nan' set to 0
                if type(ssiVal) is not np.float64:
                    #not a valid value, continue
                    continue
                else:
                    lon_lat_date_arr[lonIndex-minLon][latIndex-minLat][date] += int(ssiVal)

print ("Processed %d files!" % (count))
print (lon_lat_date_arr) 

# create a CSV file with the following columns:
# longitude | latitude | date | total radiation
with open(output_csv_file, 'w', newline='') as csvfile:
    # Define the CSV writer
    csv_writer = csv.writer(csvfile)
    
    # Write the header row
    csv_writer.writerow(['lon', 'lat', 'date', 'daily radiation'])
    
    # Iterate over the 2D array and write each entry to the CSV file
    for lon, lat_data in enumerate(lon_lat_date_arr):
        for lat, date_radiation in enumerate(lat_data):
            for date, radiation in date_radiation.items():
                #convert back from indices to longitude and latitude
                realLon = lon_start + (lon+minLon)*interval
                realLat = lat_start + (lat+minLat)*interval
                # Write the data to the CSV file
                csv_writer.writerow([realLon, realLat, date, radiation])

print("%s created successfully!" % output_csv_file)







