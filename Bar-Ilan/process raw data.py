import os
import csv
import codecs
from datetime import datetime
import pandas as pd
from itertools import zip_longest

pathToProcessedData = '/Users/alonhrl/Documents/Alon/MA-MSC/development/Bar-Ilan data'
rawDataFile = 'Solar_radiation_1h.csv'
pathToRawData = '/Users/alonhrl/Documents/Alon/MA-MSC/development/Radiation-data/Bar-Ilan'
dayRadList = []
monRadList = []
startHour = 24
endHour = 0
earliestHour = 6
latestHour = 19
startTime = datetime.strptime('09-01-2021-05:00', '%m-%d-%Y-%H:%M') # <-- set to correct start time according to first line in file
prevDate = startTime.date()

def handle_month_end():
    global monRadList
    global startHour
    global endHour
    global prevDate
    global currDate
    
    fileName = 'bar_ilan-' + str(prevDate.month).zfill(2) + '-' + str(prevDate.year)[2:] + '.csv'
    print("New month: %02d, saving to file %s, start: %d, end %d" % (currDate.date().month, fileName, startHour, endHour))
    #Create a DataFrame out of the monthly radiation list
    data = [[float(value) for value in inner_list] for inner_list in monRadList]
    #Find the maximum length among the inner lists
    max_length = max(len(inner_list) for inner_list in data)
    #Fill the gaps with zeros
    filled_data = [inner_list + [0] * (max_length - len(inner_list)) for inner_list in data]
    column_names = [str(i) for i in range(earliestHour, latestHour+1)]
    df = pd.DataFrame(filled_data, columns=column_names)
    fullPathFile = os.path.join(pathToProcessedData, fileName)
    df.to_csv(fullPathFile, index=False)
    startHour = 24
    endHour = 0
    monRadList = []
        

def handle_day_end(forDate):
    global dayRadList
    global monRadList
   
    print("New date: %s, #elements %d"%(forDate.strftime("%m/%d/%Y"), len(dayRadList)))
    #add daily radiation to monthly list
    monRadList.append(dayRadList)
    dayRadList = []
    
fullPathRawDataFile = os.path.join(pathToRawData, rawDataFile)
with codecs.open(fullPathRawDataFile, 'r', encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile)
   
    for l in reader:
        currDate = datetime.strptime(l['Date'], ' %d/%m/%y %H:%M')
        #Skip this if it is the first line in the file
        if currDate.date().month != prevDate.month and currDate != startTime:
            #first, end day and then end month
            handle_day_end(prevDate)
            handle_month_end()
            prevDate = currDate.date()
        else:
            if currDate.date() != prevDate and currDate != startTime:
                handle_day_end(prevDate)
                prevDate = currDate.date()
        
        #ignore hours earlier than 06:00 and later than 19:00
        if  (int(currDate.hour) < 6) or (int(currDate.hour) > 19):
            continue
        #ignore 'No Data' values
        if l['B_ILAN_212_1'] == 'NoData':
            continue
        #if (float(l['B_ILAN_212_1']) > 0):
        dayRadList.append(l['B_ILAN_212_1'])
        #update the earliest hour in which radiation value > 0
        if (float(l['B_ILAN_212_1']) > 0) and (int(currDate.hour) < startHour):
            startHour = int(currDate.hour)
        #update the latest hour in which radiation value > 0
        if (float(l['B_ILAN_212_1']) > 0) and (int(currDate.hour) > endHour):
            endHour = int(currDate.hour)
    
    #handle the last month
    handle_day_end(prevDate)
    handle_month_end()
