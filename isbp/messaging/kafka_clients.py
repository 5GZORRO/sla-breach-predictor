# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 10:06:54 2021

@author: Dimitris
"""

from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import NoBrokersAvailable
from runtime.handler import Handler
import logging
from config.config import Config as cnf
import json
import statistics
from datetime import datetime
import numpy as np
import pandas as pd

log = logging.getLogger(__name__)

class Consumer():
    
    consumer = None
    topics = None
    
    def init():
        global consumer
        result = None
        try:
            host = cnf.KAFKA_HOST
            port  = cnf.KAFKA_PORT
            consumer = KafkaConsumer(bootstrap_servers = host + ':' + port)
            result = 'Consumer successfully connected.'
        except NoBrokersAvailable as nba:
            consumer = None
            result = 'Error while trying to connect Consumer: ' + str(nba)
        
        return result, consumer
    
    def subscribe(topics):
        global consumer
        consumer.subscribe(topics)
    
    def set_topic(topic):
        global topics
        global consumer
        topics.append(topic)
        try:
            consumer.subscribe(topics)
            result = 'Topic list configured successfully'
        except Exception as e:
            result = 'Error: ' + str(e)
            
        return result
    
    def start():
        global topics
        global consumer
        
        for message in consumer:
            dct = message.value.decode('utf-8')
            data = json.loads(dct)
            if message.topic == 'sla':
                Handler.create_new_pipeline(data)
            else:
                data = data.get('monitoringData')
                pipeline_id = json.loads(dct).get('id')
                metric = data.get('metricValue')
                pipeline = Handler.get_active_pipeline(pipeline_id)
                if pipeline is not None: # Assume that a trained model always exists
                    pipeline.training_list.append(float(metric))
                    pipeline.prediction_list.append(float(metric))
                    date = data.get('timestamp')
                    pipeline.dates.append(date)
                    if pipeline.prediction_date is not None:
                        new_date = datetime.fromtimestamp(int(str(date)[:-5])).strftime("%d/%m/%Y %H:%M")
                        if pipeline.prediction_date == new_date:
                            pipeline.running_accuracy = pipeline.get_single_prediction_accuracy(pipeline.prediction_for_accuracy, float(metric))
                        else:
                            pipeline.running_accuracy = 0
                            pipeline.prediction_list.pop(0)
                            pipeline.prediction_list.insert(1, np.nan)
                            pipeline.prediction_list = pd.Series(pipeline.prediction_list).interpolate().tolist()
                
                    if pipeline.running_accuracy > 0: # If either the metric or the prediction is 0, the 0 accuracy cannot be included in the list
                        pipeline.accuracies.append(pipeline.running_accuracy)
                        if len(pipeline.accuracies) == pipeline.points_for_median_accuracy: # Once the list contains the defined number of accuracies, 
                                                                          # we can proceed to calculate the median
                            pipeline.median_accuracy = statistics.median(pipeline.accuracies)
                            log.info('Median accuacy is: {0}'.format(pipeline.median_accuracy))
                            pipeline.accuracies.pop(0) # Remove the first accuracy in the list in order to insert the one in the next iteration at the back
                    if len(pipeline.prediction_list) == pipeline.n_steps:
                        dictionary = {'pipeline_id' : pipeline.id, 'timestamp' : date, 'data' : pipeline.prediction_list}
                        with open(cnf.TEMP_FILE_PATH + 'data.json', 'w') as outfile:
                            json.dump(dictionary, outfile)
                            pipeline.prediction_list.pop(0)
           
                    if pipeline.median_accuracy < cnf.GLOBAL_ACCURACY:
                        if len(pipeline.training_list) == cnf.TRAIN_DATA_POINTS:
                            pd.DataFrame(pipeline.training_list).to_csv(cnf.TEMP_FILE_PATH + 'train.csv')
                            pipeline.training_list = pipeline.training_list[cnf.TRAIN_DATA_POINTS:]
                        
                        
                    
    def transform(plist, features):
        X = np.array([plist])
        inp = X.reshape((X.shape[0], X.shape[1], features))
        return inp
                
    def stop():
       global consumer
       result = None
       try:
           consumer.unsubscribe()
           consumer.close(autocommit = False)
           result = 'Consumer successfully shut down'
       except Exception as e:
          result = 'Exception: ' +str(e)
        
       return result

class Producer():
    
    producer = None
    
    def init():
        global producer
        result = None
        try:
            host = cnf.KAFKA_HOST
            port  = cnf.KAFKA_PORT
            producer = KafkaProducer(bootstrap_servers = host + ':' + port)
            result = 'Producer successfully connected.'
        except NoBrokersAvailable as nba:
            result = 'Error while trying to connect Producer: ' + str(nba)
        
        return result
    
    def send(data):
        global producer
        producer.send(cnf.BREACH_TOPIC, data.encode('utf-8'))
            