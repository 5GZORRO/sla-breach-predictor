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
            try:
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
                    date = data.get('timestamp')
                    log.info('Received metric {0} with slice ID {1}'.format(metric, pipeline_id))
                    pipeline = Handler.get_active_pipeline(pipeline_id)
                    if pipeline is not None:
                        pipeline.try_insert(metric, date)
                        if list(pipeline.selection_predictions.values())[0] != 0:
                            pipeline.get_single_prediction_accuracy(metric)              
                        if pipeline.current_model is not None:
                            if len(pipeline.selection_accuracies.get(pipeline.current_model._id)) == pipeline.points_for_median_accuracy: 
                                pipeline.median_accuracy = pipeline.calculate_median_accuracy()
                        if pipeline.current_model != None and pipeline.median_accuracy > 0.0 and pipeline.median_accuracy < cnf.GLOBAL_ACCURACY:
                            dictionary = {'model': pipeline.current_model._id,
                                          'class': pipeline.current_model._class,
                                          'pipeline': pipeline.transactionID}
                            with open(cnf.TEMP_FILE_PATH + pipeline.transactionID+'-model.json', 'w') as outfile:
                                json.dump(dictionary, outfile)
                            log.info('Launching training job for {0} and model {1}'.format(pipeline.transactionID, pipeline.current_model._id))
                            pipeline.median_accuracy = 0.0
                            pipeline.clear_predictions()
                            pipeline.isBlocked = True
                        if len(pipeline.prediction_list) == pipeline.n_steps:
                            pipeline.request_prediction(date)
            except Exception as e:
                log.error(e)
                    
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
            topic = cnf.BREACH_TOPIC
            producer = KafkaProducer(bootstrap_servers = host +':' +port)
            result = 'Producer successfully connected.'
        except NoBrokersAvailable as nba:
            result = 'Error while trying to connect Producer: ' + str(nba)
        
        return result
    
    def send(data):
        global producer
        global topic
        producer.send(topic, data.encode('utf-8'))

    
    
    