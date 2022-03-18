#!/usr/bin/env python

import configparser
import requests

# INITIALIZE ENVIRONMENT

config = configparser.ConfigParser()
config.read('config.env')
API_URL = config.get('API','API_URL')
CAPMC_TOKEN = config.get('CAPMC','CAPMC_TOKEN')

payload = '[{"study_id":3,"first_name":"Stevie", "last_name":"Wonder","dob":"02-14-1954", "dob_2":"1954-02-14"}]'


data = {
    'token': CAPMC_TOKEN,
    'content': 'record',
    'format': 'json',
    'type': 'flat',
    'overwriteBehavior': 'normal',
    'data': payload,
    'returnContent': 'count',
    'returnFormat': 'json'
}

r = requests.post(API_URL, data=data)
print(r.json())
