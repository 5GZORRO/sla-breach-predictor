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
        log.info('New consumer thread started')
        for message in consumer:
            dct = message.value.decode('utf-8')
            data = json.loads(dct)
            if message.topic == 'isbp-topic':
                transactionID = data.get('transactionID')
                if data.get('eventType') == 'new_SLA':
                    log.info('Received new SLA event with transaction ID: {0}'.format(transactionID))
                    pipeline = Handler.create_new_pipeline(data)
                elif data.get('eventType') == 'new_SLA_ACK':
                    log.info('Received instantiation acknowledgement with transaction ID: {0}'.format(transactionID))
                    pipeline = Handler.get_active_pipeline(transactionID)
                    pipeline.waiting_on_ack = False
            else:
                data = data.get('monitoringData')
                pipeline_id = data.get('transactionID')
                metric = data.get('metricValue')
                log.info(data)
                pipeline = Handler.get_active_pipeline(pipeline_id)
                if pipeline is not None:
                        pipeline.training_list.append(float(metric))
                        if not pipeline.waiting_on_ack:
                            pipeline.prediction_list.append(float(metric))
                        date = data.get('timestamp')
                        pipeline.dates.append(date)
                        # if pipeline.prediction_date is not None:
                        #     new_date = datetime.fromtimestamp(int(str(date)[:-5])).strftime("%d-%m-%YT%H:%M")
                        #     if pipeline.prediction_date == new_date:
                        #         pipeline.running_accuracy = pipeline.get_single_prediction_accuracy(pipeline.prediction_for_accuracy, float(metric))
                            # else:
                            #         pipeline.running_accuracy = 0
                            #         pipeline.prediction_list.pop(0)
                            #         pipeline.prediction_list.insert(1, np.nan)
                            #         pipeline.prediction_list = pd.Series(pipeline.prediction_list).interpolate().tolist()
                
                        if pipeline.running_accuracy > 0: # If either the metric or the prediction is 0, the 0 accuracy cannot be included in the list
                            pipeline.accuracies.append(pipeline.running_accuracy)
                            if len(pipeline.accuracies) == pipeline.points_for_median_accuracy: 
                                pipeline.median_accuracy = statistics.median(pipeline.accuracies)
                                log.info('Median accuracy is: {0}'.format(pipeline.median_accuracy))
                                pipeline.accuracies.pop(0) # Remove the first accuracy in the list in order to insert the one in the next iteration at the back
                        if len(pipeline.prediction_list) == pipeline.n_steps:
                            log.info('Launching prediction job...')
                            dictionary = {'transactionID': pipeline.transactionID,
                                          'instanceID' : pipeline.instanceID,
                                          'productID' : pipeline.productID,
                                          'metric': pipeline.metric,
                                          'model' : pipeline.model,
                                          'timestamp' : date,
                                          'data' : pipeline.prediction_list,
                                          'place' : pipeline.location}
                            with open(cnf.TEMP_FILE_PATH + 'data.json', 'w') as outfile:
                                json.dump(dictionary, outfile)
                            pipeline.prediction_list.pop(0)
           
                    # if pipeline.median_accuracy < cnf.GLOBAL_ACCURACY:
                    #     if len(pipeline.training_list) == cnf.TRAIN_DATA_POINTS:
                    #         dictionary = {'metric': pipeline.metric}    
                    #         with open(cnf.TEMP_FILE_PATH + 'metric.json', 'w') as outfile:
                    #             json.dump(dictionary, outfile)
                    #         pd.DataFrame(pipeline.training_list).to_csv(cnf.TEMP_FILE_PATH + 'train.csv')
                    #         pipeline.training_list = pipeline.training_list[cnf.TRAIN_DATA_POINTS:]
                        else:
                            log.info('Monitoring data discarded from prediction list')
                        
                    
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
    topic = None
    
    def init():
        global producer
        global topic
        result = None
        try:
            host = cnf.KAFKA_HOST
            port  = cnf.KAFKA_PORT
            producer = KafkaProducer(bootstrap_servers = host +':' +port)
            result = 'Producer successfully connected.'
        except NoBrokersAvailable as nba:
            result = 'Error while trying to connect Producer: ' + str(nba)
        
        return result
    
    def send(data):
        global producer
        global topic
        producer.send('isbp-topic-out', data.encode('utf-8'))

    
    
    