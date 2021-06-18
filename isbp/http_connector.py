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
payload = '{"userId" : "isbp", "authToken" : "blah"}'
headers = {'Content-type': 'application/json'}


def poll():
    
    while(True):
        pipelines = Handler.get_list()
        for pID in pipelines:
            pipeline = pipelines.get(pID)
            r = requests.get(catalog_url+pipeline.productID, json={"userId": "isbp", "authToken" : "blah"})
            if r.status_code == 200:
              logging.info('Successfully retrieved monitoring data for pipeline: {0}'.format(pipeline.productID))
              data_list = json.loads(r.text)
              last_item = data_list[len(data_list)-1]
              if last_item.get('timestamp') != pipeline.current_timestamp:
                      pipeline.current_timestamp = last_item.get('timestamp')
                      metric_value = float(last_item.get('metricvalue'))
                      logging.info('Received metric {0}'.format(metric_value))
                      metric_value = Handler.inverse_transform(100-metric_value)
                      pipeline.training_list.append(metric_value)
                      pipeline.prediction_list.append(metric_value)
                      date = last_item.get('timestamp')
                      pipeline.dates.append(date)
                      # if pipeline.prediction_date is not None:
                      #   new_date = datetime.fromtimestamp(int(date[:-5])).strftime("%d-%m-%YT%H:%M")
                      #   if pipeline.prediction_date == new_date:
                      #       pipeline.running_accuracy = pipeline.get_single_prediction_accuracy(pipeline.prediction_for_accuracy, metric_value)
                      #   else:
                      #       pipeline.running_accuracy = 0
                      #       pipeline.prediction_list.pop(0)
                      #       pipeline.prediction_list.insert(1, np.nan)
                      #       pipeline.prediction_list = pd.Series(pipeline.prediction_list).interpolate().tolist()
                
                      # if pipeline.running_accuracy > 0: # If either the metric or the prediction is 0, the 0 accuracy cannot be included in the list
                      #     pipeline.accuracies.append(pipeline.running_accuracy)
                      #     if len(pipeline.accuracies) == pipeline.points_for_median_accuracy: # Once the list contains the defined number of accuracies, 
                      #                                                     # we can proceed to calculate the median
                      #       pipeline.median_accuracy = statistics.median(pipeline.accuracies)
                      #       logging.info('Median accuracy is: {0}'.format(pipeline.median_accuracy))
                      #       pipeline.accuracies.pop(0) # Remove the first accuracy in the list in order to insert the one in the next iteration at the back
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
                            logging.info('Launching prediction!!!')
                            pipeline.prediction_list.pop(0)
            else:
              logging.info('Failed to get monitoring data for pipeline: {0}'.format(pipeline.productID))
              
        time.sleep(10)