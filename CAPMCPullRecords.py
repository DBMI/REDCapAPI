#!/usr/bin/env python

import configparser
from datetime import datetime
import numpy as np
import pandas as pd
import re
import requests
import time
 

# INITIALIZE ENVIRONMENT

config = configparser.ConfigParser()
config.read('config.env')
API_URL = config.get('API','API_URL')
CAPMC_TOKEN = config.get('CAPMC','CAPMC_TOKEN')

RECORDS_PER_PAYLOAD = 10


# CONVERT VARIOUS FORMATS OF DATES TO A DATETIME OBJECT

def convert_to_date(date_string):
    
    date_string = date_string.strip().replace(r" [\d]{2}:[\d]{2}:[\d]{2}", "")

    if date_string == "":
        return None
    elif re.match(r"[\d]{1,2}/[\d]{1,2}/[\d]{4}", date_string):                         # Match 01/31/1970
        return datetime.strptime(date_string, '%m/%d/%Y')
    elif re.match(r"[\d]{1,2}/[\d]{1,2}/[\d]{2}", date_string):                         # Match 01/31/70
        return datetime.strptime(date_string, '%m/%d/%y')
    elif re.match(r"[\d]{1,2}-[\d]{1,2}-[\d]{4}", date_string):                         # Match 01-31-1970
        return datetime.strptime(date_string, '%m-%d-%Y')
    elif re.match(r"[\d]{1,2}-[\d]{1,2}-[\d]{2}", date_string):                         # Match 01-31-70
        return datetime.strptime(date_string, '%m-%d-%y')
    elif re.match(r"[\d]{4}-[\d]{1,2}-[\d]{1,2} [\d]{2}:[\d]{2}:[\d]{2}", date_string): # Match 1970-01-31 12:05:10
        return datetime.strptime(date_string, '%Y-%m-%d  %H:%M:%S')
    elif re.match(r"[\d]{4}-[\d]{1,2}-[\d]{1,2}", date_string):                         # Match 1970-01-31
        return datetime.strptime(date_string, '%Y-%m-%d')
    elif re.match(r"[\d]{1,2} [A-Z]{1}[a-z]{2} [\d]{4}", date_string):                  # Match 31 Jan 1970
        return datetime.strptime(date_string, '%d %b %Y')
    elif re.match(r"[A-Z]{1}[a-z]{2} +[\d]{1,2} [\d]{4} 12:00AM", date_string):         # Match Jan 31 1970 12:00AM
        return datetime.strptime(date_string.replace(" 12:00AM", ""), '%b %d %Y')
    else:
        print("WE HAVE A PROBLEM WITH THIS DATE: ", date_string)
        return None


# BUILD A SINGLE JSON ENTRY FOR THE PAYLOAD OBJECT

def get_payload_entry(study_id, dob, pcd, cpd, dla):
    if dob == None and pcd == None and cpd == None and dla == None:
        return ""
    else:
        payload_entry = "{\"study_id\":" + study_id
        if dob != None:
            payload_entry = payload_entry + ",\"dob_2\":\"" + dob.strftime("%Y-%m-%d") + "\""
        if pcd != None:
            payload_entry = payload_entry + ",\"primary_consent_date_2\":\"" + pcd.strftime("%Y-%m-%d") + "\""
        if cpd != None:
            payload_entry = payload_entry + ",\"core_participant_date_2\":\"" + cpd.strftime("%Y-%m-%d") + "\""
        if dla != None:
            payload_entry = payload_entry + ",\"date_of_last_activity_2\":\"" + dla.strftime("%Y-%m-%d") + "\""
        payload_entry = payload_entry + "}"
        return payload_entry


# PROCCESS THE PAYLOAD (PRINT AND SUBMIT TO API)

def process_payload(payload):
    data_push = {
        'token': CAPMC_TOKEN,
        'content': 'record',
        'format': 'json',
        'type': 'flat',
        'overwriteBehavior': 'normal',
        'data': payload,
        'returnContent': 'count',
        'returnFormat': 'json'
    }
    print(data_push)
    print()
    time.sleep(0.01)



# RETRIEVE STUDY IDS AND DATES FROM THE REDCAP API (CAPMC)

data_pull = {
    'token': CAPMC_TOKEN,
    'content': 'record',
    'format': 'json',
    'type': 'flat',
    'csvDelimiter': '',
    #'records[0]': '6345948',
    #'records[1]': '6345957',
    #'records[2]': '6345965',
    #'records[3]': '6345966',
    #'records[4]': '6345949',
    'fields[0]': 'study_id',
    'fields[1]': 'dob',
    'fields[2]': 'primary_consent_date',
    'fields[3]': 'core_participant_date',
    'fields[4]': 'date_of_last_activity',
    'rawOrLabel': 'raw',
    'rawOrLabelHeaders': 'raw',
    'exportCheckboxLabel': 'false',
    'exportSurveyFields': 'false',
    'exportDataAccessGroups': 'false',
    'returnFormat': 'json'
}

r = requests.post(API_URL, data=data_pull)
dates_df = pd.json_normalize(r.json())

count_total = 0
count_with_dates = 0

for i in dates_df.index:
    count_total+=1
    dob = convert_to_date(dates_df['dob'][i])
    pcd = convert_to_date(dates_df['primary_consent_date'][i])
    cpd = convert_to_date(dates_df['core_participant_date'][i]) 
    dla = convert_to_date(dates_df['date_of_last_activity'][i])
    payload_entry = get_payload_entry(dates_df['study_id'][i], dob, pcd, cpd, dla)
    if payload_entry != "":
        count_with_dates+=1
        if count_with_dates % RECORDS_PER_PAYLOAD == 1:
            payload = "[" + payload_entry + ", "
        elif (count_with_dates % RECORDS_PER_PAYLOAD == 0) or (count_total == dates_df.shape[0]):
            payload = payload + payload_entry + "]"
            process_payload(payload)
        else:
            payload = payload + payload_entry + ", "


print(dates_df.shape[0])
print(count_total)
print(count_with_dates)

# CODE FOR TESTING THE CONVERT TO DATE FUNCTION

#date = ""
#print(date)
#print(convert_to_date(date))
#print()

#date = "01/31/1970"
#print(date)
#print(convert_to_date(date))
#print()

#date = "01/31/70"
#print(date)
#print(convert_to_date(date))
#print()

#date = "01-31-1970"
#print(date)
#print(convert_to_date(date))
#print()

#date = "01-31-70"
#print(date)
#print(convert_to_date(date))
#print()

#date = "1970-01-31"
#print(date)
#print(convert_to_date(date))
#print()

#date = "31 Jan 1970"
#print(date)
#print(convert_to_date(date))
#print()

#date = "Jan 31 1970 12:00AM"
#print(date)
#print(convert_to_date(date))
#print()
