import json
import requests
from datetime import datetime, timedelta
import csv

#! the following request is a list of all stations
#url = "https://api.ims.gov.il/v1/Envista/stations"

#! Bet-Dagan RAD station id is 85; the following request is daily data from station-id 85 (same day)
#url = "https://api.ims.gov.il/v1/envista/stations/85/data/daily"

#! Bet-Dagan RAD station id is 85; the following request is data from station-id 85 between dates
url = "https://api.ims.gov.il/v1/envista/stations/85/data?from=2021/09/01&to=2021/09/02"

#! Bet-Dagan RAD station id is 85; the following request is data from station-id 85 for specific date 
#url = "https://api.ims.gov.il/v1/envista/stations/85/data/daily/2021/09/01"

#! Bet-Dagan RAD station id is 85; 'Global rad' is channel 7; the following request is daily global-rad from Bet-Dagan 
#url = "https://api.ims.gov.il/v1/envista/stations/85/data/7/daily"

#! Bet-Dagan station id for temp is 54; Ground temp (TG) is channel 11; the following request is daily ground temp from Bet-Dagan
#url = "https://api.ims.gov.il/v1/envista/stations/54/data/11/daily"


#this is the token received via mail on 06/07/23
headers = {"Authorization": "ApiToken f058958a-d8bd-47cc-95d7-7ecf98610e47"}

response = requests.request("GET", url, headers=headers)
data= json.loads(response.text.encode('utf8'))

""" #! print 'TG' (ground temp) full data per day (10 minutes resolution); calendaric order (early-->later)
sorted_data = sorted(data["data"], key=lambda x: x["datetime"])

for item in sorted_data:
    datetime = item["datetime"]
    channels = item["channels"]
    
    for channel in channels:
        if channel["name"] == "TG":
            value = channel["value"]
            print(f"{datetime}, {value}") """

""" #! print 'Grad' (global radiation) full data per day (10 minutes resolution); calendaric order (early-->later)
sorted_data = sorted(data["data"], key=lambda x: x["datetime"])

for item in sorted_data:
    datetime = item["datetime"]
    channels = item["channels"]
    
    for channel in channels:
        if channel["name"] == "Grad":
            value = channel["value"]
            print(f"{datetime}, {value}") """


#! print aggregated hourly data per day for dates interval
#! IMPORTANT:
#!  According to the IMS, in order to get the accumulated radiation per day
#!  need to divide the sum off all reade by 6 !!!
#!  [source: https://ims.gov.il/sites/default/files/2022-09/%D7%90%D7%95%D7%93%D7%95%D7%AA%20%D7%9E%D7%90%D7%92%D7%A8%20%D7%A0%D7%AA%D7%95%D7%A0%D7%99%D7%9D%20%D7%A2%D7%A9%D7%A8%20%D7%93%D7%A7%D7%AA%D7%99%D7%99%D7%9D.pdf] 
startDate = "2022/01/01"
endDate = "2022/01/08"
stationId = "85"


headers = {"Authorization": "ApiToken f058958a-d8bd-47cc-95d7-7ecf98610e47"}



stationIds = [85,8,10,22,29,30,32,33,43,58,60,64,69,206,380,381,499]

daily_rad_sum = {}
hourly_grad_sum = {}  # Dictionary to store aggregated 'Grad' values for each hour
daily_sum = 0
ims_datetime_format = "%Y-%m-%dT%H:%M:%S%z"
dummy_date  = datetime.strptime(startDate, "%Y/%m/%d")  # Convert string to datetime object

for station in stationIds:
    day_before_interval = current_date = (dummy_date - timedelta(days=1)).date()  # Subtract one day from the datetime object
    url = f"https://api.ims.gov.il/v1/envista/stations/{station}/data?from={startDate}&to={endDate}"
    response = requests.request("GET", url, headers=headers)
    if response.status_code != 200:
        continue

    data= json.loads(response.text.encode('utf8'))
    url = f"https://api.ims.gov.il/v1/envista/stations/{station}"
    response = requests.request("GET", url, headers=headers)
    stationData = json.loads(response.text.encode('utf8'))
    stationName = stationData['name']
    lat = stationData['location']['latitude']
    lon = stationData['location']['longitude']
    print("processing station %s ..." % stationName)
   

    for entry in data['data']:
        datetime_str = entry['datetime']
        date_time_from_ims_format = datetime.strptime(datetime_str, ims_datetime_format)
        datetime_parts = datetime_str.split('T')
        date, time = datetime_parts[0], datetime_parts[1]
        hour = time[:2]
        
        if date_time_from_ims_format.date() != current_date:
            if current_date != day_before_interval:
                daily_rad_sum[current_date] = daily_sum
                daily_sum = 0
                current_date = date_time_from_ims_format.date()
            else:
                current_date = date_time_from_ims_format.date()
                continue
    
        channels = entry['channels']
        for channel in channels:
            if channel['name'] == 'Grad':
                daily_sum += channel['value']

    #handle last day
    daily_rad_sum[current_date] = daily_sum

    #write to a file
    csv_file_path = stationName + "-" +'radiation_data.csv'  # Output CSV file path

    with open(csv_file_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Date', 'Radiation'])  # Write header row
        writer.writerow(['latitude', lat])
        writer.writerow(['longitude', lon])
        for day, rad in daily_rad_sum.items():
            print("%s: %d W*h/m2" % (day, int(rad/6)))
            writer.writerow([day, int(rad/6)])  # Write each date and radiation value as a row

    print("%s created successfully!" % csv_file_path)


""" #! print aggregated hourly data per day
#! IMPORTANT:
#!  According to the IMS, in order to get the accumulated radiation per day
#!  need to divide the sum off all reade by 6 !!!
#!  [source: https://ims.gov.il/sites/default/files/2022-09/%D7%90%D7%95%D7%93%D7%95%D7%AA%20%D7%9E%D7%90%D7%92%D7%A8%20%D7%A0%D7%AA%D7%95%D7%A0%D7%99%D7%9D%20%D7%A2%D7%A9%D7%A8%20%D7%93%D7%A7%D7%AA%D7%99%D7%99%D7%9D.pdf] 
hourly_grad_sum = {}  # Dictionary to store aggregated 'Grad' values for each hour
daily_sum = 0

for entry in data['data']:
    datetime_str = entry['datetime']
    datetime_parts = datetime_str.split('T')
    date, time = datetime_parts[0], datetime_parts[1]
    hour = time[:2]
    
    channels = entry['channels']
    for channel in channels:
        if channel['name'] == 'Grad':
            value = channel['value']
            if hour in hourly_grad_sum:
                hourly_grad_sum[hour] += value
            else:
                hourly_grad_sum[hour] = value

# Print the aggregated 'Grad' value for each hour
date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
formatted_date = date_obj.strftime("%d-%m-%Y")
for hour, value in hourly_grad_sum.items():
    print(f"{hour}, {value}")
    daily_sum += value

print("Aggregated global radiation per %s: %d W*h/m2" % (formatted_date, int(daily_sum/6))) """
            