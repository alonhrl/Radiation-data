import eumdac
import datetime
import sys
import os

# Insert your personal key and secret into the single quotes
consumer_key = 'f41HR6Zfq4LRU8p5feSh8bGMaxUa'
consumer_secret = 'VIR1k58d_zHoUgkfneFIchv9u6Aa'

credentials = (consumer_key, consumer_secret)

token = eumdac.AccessToken(credentials)

print(f"This token '{token}' expires {token.expiration}")

datastore = eumdac.DataStore(token)
datastore.collections

for collection in datastore.collections:
    print(f"{collection} - {collection.title}")

original_stdout = sys.stdout 	

outFileName = 'collections-list.txt'
with open(outFileName, 'w') as f:
    sys.stdout = f
    for collection in datastore.collections:
        print(f"{collection} - {collection.title}")
    # Reset the standard output
    sys.stdout = original_stdout
    print("Collections were written to: " + os.getcwd()+'/'+outFileName)

""" selected_collection = datastore.get_collection('EO:EUM:DAT:MSG:HRSEVIRI')

# Add vertices for polygon, wrapping back to the start point.
geometry = [[-1.0, -1.0],[4.0, -4.0],[8.0, -2.0],[9.0, 2.0],[6.0, 4.0],[1.0, 5.0],[-1.0, -1.0]]

# Set sensing start and end time
start = datetime.datetime(2021, 11, 10, 8, 0)
end = datetime.datetime(2021, 11, 10, 9, 0)

# Retrieve datasets that match our filter
products = selected_collection.search(
    geo='POLYGON(({}))'.format(','.join(["{} {}".format(*coord) for coord in geometry])),
    dtstart=start, 
    dtend=end)
  
print(f'Found Datasets: {len(products)} datasets for the given time range') 

for product in products:
    print(str(product)) """