import json
import requests
import datetime

#! the following request is a list of all stations
#url = "https://api.ims.gov.il/v1/Envista/stations"

#! Bet-Dagan RAD station id is 85; the following request is daily data from station-id 85 (same day)
#url = "https://api.ims.gov.il/v1/envista/stations/85/data/daily"

#! Bet-Dagan RAD station id is 85; the following request is data from station-id 85 between dates
#url = "https://api.ims.gov.il/v1/envista/stations/85/data?from=2021/09/01&to=2021/09/02"

#! Bet-Dagan RAD station id is 85; the following request is data from station-id 85 for specific date 
url = "https://api.ims.gov.il/v1/envista/stations/85/data/daily/2021/09/01"

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


#! print aggregated hourly data per day
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

print("Aggregated global radiation per %s: %d W*h/m2" % (formatted_date, int(daily_sum/6)))
            