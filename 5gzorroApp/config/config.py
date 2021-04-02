# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 12:44:11 2021

@author: Dimitris
"""

from configparser import ConfigParser

class Config():
    
    __conf = None
    
    #OPERATIONS
    TR_TMT = 0
    W_TMT = 0
    PRD_TMT = 0
    
    #MODEL
    LOGS = None
    SAVE = None
    DATA = None
    TRAIN_DATA_POINTS = 0
    
    #KAFKA
    KAFKA_HOST = None
    KAFKA_PORT = 0
    KAFKA_POLL_TIMEOUT = 0
    MON_TOPIC = None
    BREACH_TOPIC = None
    
    
    def load_configuration():
        global __conf
        __conf = ConfigParser()
        __conf.read('properties.conf')
        
        Config.PRD_TMT = int(__conf['operations']['predict_timeout'])
        Config.TR_TMT = int(__conf['operations']['train_timeout'])
        Config.W_TMT = int(__conf['operations']['wait_predict'])
        
        Config.LOGS  = __conf['model']['logs_path']
        Config.SAVE = __conf['model']['save_path']
        Config.DATA = __conf['model']['data_path']
        Config.TRAIN_DATA_POINTS = int(__conf['model']['train_data_points'])
        
        Config.KAFKA_HOST = __conf['kafka']['host']
        Config.KAFKA_PORT = __conf['kafka']['port']
        Config.KAFKA_POLL_TIMEOUT = int(__conf['kafka']['poll_timeout'])
        Config.MON_TOPIC = __conf['kafka']['mon_topic']
        Config.BREACH_TOPIC = __conf['kafka']['breach_topic']
        
        