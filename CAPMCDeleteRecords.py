#!/usr/bin/env python

import configparser
import requests

config = configparser.ConfigParser()
config.read('config.env')
API_URL = config.get('API','API_URL')
CAPMC_TOKEN = config.get('CAPMC','CAPMC_TOKEN')

data = {
    'token': CAPMC_TOKEN,
    'action': 'delete',
    'content': 'record',
    'format': 'json',
    'type': 'flat',
    'csvDelimiter': '',
    'records[0]': '3',
    'rawOrLabel': 'raw',
    'rawOrLabelHeaders': 'raw',
    'exportCheckboxLabel': 'false',
    'exportSurveyFields': 'false',
    'exportDataAccessGroups': 'false',
    'returnFormat': 'json'
}

r = requests.post(API_URL, data=data)
print(r.json())
