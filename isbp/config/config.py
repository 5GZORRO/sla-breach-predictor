# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 12:44:11 2021

@author: Dimitris
"""

from configparser import ConfigParser

class Config():
    
    __conf = None
    
    # MODEL
    GLOBAL_ACCURACY = 0
    TRAIN_DATA_POINTS = 0
    POINTS_FOR_MEDIAN_ACCURACY = 0
    
    # KAFKA
    KAFKA_HOST = None
    KAFKA_PORT = 0
    TOPICS = ['isbp-topic']
    BREACH_TOPIC = None
    MON_DATA_TOPIC = None
    
    # STORAGE
    TEMP_FILE_PATH = None
    
    
    def load_configuration():
        global __conf
        __conf = ConfigParser()
        __conf.read('properties.conf')
        
        Config.GLOBAL_ACCURACY = int(__conf['model']['global_accuracy'])
        Config.TRAIN_DATA_POINTS = int(__conf['model']['train_data_points'])
        Config.POINTS_FOR_MEDIAN_ACCURACY = int(__conf['model']['points_for_median_accuracy'])
        
        Config.KAFKA_HOST = __conf['kafka']['host']
        Config.KAFKA_PORT = __conf['kafka']['port']
        mon_data_topic = __conf['kafka']['mon_topic']
        if mon_data_topic != "":
            Config.TOPICS.append(mon_data_topic)
            Config.MON_DATA_TOPIC = mon_data_topic
            
        Config.BREACH_TOPIC = __conf['kafka']['breach_topic']
        
        Config.TEMP_FILE_PATH = __conf['storage']['temp_file_path']
        
        
        