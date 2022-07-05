# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 12:44:11 2021

@author: Dimitris
"""

from configparser import ConfigParser

class Config():
    
    __conf = None
    
    # OPERATIONS
    TRAIN_DATA_POINTS = 0
    POINTS_FOR_MEDIAN_ACCURACY = 0
    GLOBAL_ACCURACY = 0
    PREDICTIONS_MODEl_SELECTION = 0
    
    # KAFKA
    KAFKA_HOST = None
    KAFKA_PORT = 0
    TOPICS = ['isbp-topic']
    BREACH_TOPIC = None
    MON_DATA_TOPIC = None
    
    #CONNECTORS
    DATALAKE = None
    DATALAKE_STREAM = None
    LCM = None
    
    def load_configuration():
        global __conf
        __conf = ConfigParser()
        __conf.read('properties.conf')
        operations = __conf['operations']
        kafka = __conf['kafka']
        connectors = __conf['connectors']
        
        Config.GLOBAL_ACCURACY = float(__conf['operations']['global_accuracy'])
        Config.TRAIN_DATA_POINTS = int(__conf['operations']['train_data_points'])
        Config.POINTS_FOR_MEDIAN_ACCURACY = int(__conf['operations']['points_for_median_accuracy'])
        Config.MODEL_SELECTION_PREDICTIONS = int(__conf['operations']['model_selection_predictions'])
        
        Config.KAFKA_HOST = kafka['host']
        
        if kafka['port'] != '':
            Config.KAFKA_PORT = int(kafka['port'])
        mon_data_topic = kafka['mon_topic']
        if mon_data_topic != "":
            Config.TOPICS.append(mon_data_topic)
            Config.MON_DATA_TOPIC = mon_data_topic  
        Config.BREACH_TOPIC = kafka['breach_topic']
        
        Config.DATALAKE = connectors['datalake']
        Config.LCM = connectors['lcm']
        
        
        
        