# -*- coding: utf-8 -*-
"""
Created on Thu Jun 10 14:43:46 2021

@author: dlaskaratos
"""

import time
from runtime.handler import Handler
from config.config import Config as cnf
import requests
import json
import logging
from datetime import datetime
import numpy as np
import pandas as pd
import statistics

kafka_url = 'http://172.28.3.196:9092'
catalog_url = 'http://172.28.3.46:30342/datalake/v1/catalog/product/'

def poll():
    
    while(True):
        pipelines = Handler.get_list()
        for pID in pipelines:
            pipeline = pipelines.get(pID)
            r = requests.get(catalog_url+pipeline.productID, json={"userId": "isbp", "authToken" : "blah"})
            if r.status_code == 200:
              # logging.info('Successfully retrieved monitoring data for pipeline: {0}'.format(pipeline.productID))
              data_list = json.loads(r.text)
              last_item = data_list[len(data_list)-1]
              if last_item.get('timestamp') != pipeline.current_timestamp:
                      pipeline.current_timestamp = last_item.get('timestamp')
                      value = last_item.get('metricvalue')
                      if value is not None:
                          metric_value = float(value)
                          logging.info('Received metric {0}'.format(metric_value))
                          metric_value = Handler.inverse_transform(100-metric_value)
                          pipeline.training_list.append(metric_value)
                          pipeline.prediction_list.append(metric_value)
                          date = last_item.get('timestamp')
                          pipeline.dates.append(date)
                      if len(pipeline.prediction_list) == pipeline.n_steps:
                        dictionary = {'slaID' : pipeline.productID,
                                      'transactionID' : pipeline.transactionID,
                                      'productID' : pipeline.productID,
                                      'resourceID' : pipeline.resourceID,
                                      'instanceID' : pipeline.instanceID,
                                      'ruleID' : pipeline.metric,
                                      'metric' : pipeline.metricLink,
                                      'timestamp' : date,
                                      'data' : pipeline.prediction_list}
                        with open(cnf.TEMP_FILE_PATH + 'data.json', 'w') as outfile:
                            json.dump(dictionary, outfile)
                            logging.info('LAUNCHING PREDICTION')
                            pipeline.prediction_list.pop(0)
            else:
              logging.info('Failed to get monitoring data for pipeline: {0}'.format(pipeline.productID))
              
        time.sleep(10)