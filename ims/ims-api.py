import json
import requests

#! the following request is a list of all stations
#url = "https://api.ims.gov.il/v1/Envista/stations"

#! Bet-Dagan station id is 85; the following request is daily data from station-id 85 (same day)
#url = "https://api.ims.gov.il/v1/envista/stations/85/data/daily"

#! Bet-Dagan station id is 85; the following request is data from station-id 85 for the 01-9-21
#url = "https://api.ims.gov.il/v1/envista/stations/85/data?from=2021/09/01&to=2021/09/02"

#! Bet-Dagan station id is 85; 'Global rad' is channel 7; the following request is daily global-rad from Bet-Dagan 
url = "https://api.ims.gov.il/v1/envista/stations/85/data/7/daily"


#this is the token received via mail on 06/07/23
headers = {"Authorization": "ApiToken f058958a-d8bd-47cc-95d7-7ecf98610e47"}

response = requests.request("GET", url, headers=headers)
data= json.loads(response.text.encode('utf8'))

""" #! print full data per day (10 minutes resolution); calendaric order (early-->later)
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
hourly_grad_sum = {}  # Dictionary to store aggregated 'Grad' values for each hour

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
for hour, value in hourly_grad_sum.items():
    print(f"{hour}, {value}")
            