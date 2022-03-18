#!/usr/bin/env python

import configparser
config = configparser.ConfigParser()
config.read('config.env')

print(config.get('API','API_URL'))
print(config.get('CAPMC','CAPMC_TOKEN'))