# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 12:44:11 2021

@author: Dimitris
"""

from configparser import ConfigParser

class Config():
    
    __conf = None
    TR_TMT = 0
    W_TMT = 0
    PRD_TMT = 0
    KAFKA_HOST = None
    KAFKA_PORT = 0
    KAFKA_POLL_TIMEOUT = 0
    MON_TOPIC = None
    BREACH_TOPIC = None
    LOGS = None
    SAVE = None
    DATA = None
    
    
    def load_configuration():
        global __conf
        __conf = ConfigParser()
        __conf.read('properties.conf')
        
        Config.PRD_TMT = int(__conf['operations']['predict_timeout'])
        Config.TR_TMT = int(__conf['operations']['train_timeout'])
        Config.W_TMT = int(__conf['operations']['wait_predict'])
        Config.KAFKA_HOST = __conf['kafka']['host']
        Config.KAFKA_PORT = __conf['kafka']['port']
        Config.KAFKA_POLL_TIMEOUT = int(__conf['kafka']['poll_timeout'])
        Config.MON_TOPIC = __conf['kafka']['mon_topic']
        Config.BREACH_TOPIC = __conf['kafka']['breach_topic']
        Config.LOGS  = __conf['model']['logs_path']
        Config.SAVE = __conf['model']['save_path']
        Config.DATA = __conf['model']['data_path']
        
        
    
    def get_property(group: str, prop: str):
        global __conf
        return __conf[group][prop]
        