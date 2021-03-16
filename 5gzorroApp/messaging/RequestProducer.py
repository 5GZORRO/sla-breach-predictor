# -*- coding: utf-8 -*-
"""
Created on Wed Dec 16 11:34:30 2020d

@author: Dimitris
"""

from kafka import KafkaProducer
from pandas import DataFrame

# TODO: Load configuration from file
# TODO: consumer and producer must inherit from kafkaclient
# TODO: consumer must poll data from server

class kafkaClient():
    
    __kafka_server_ip = None
    __kafka_subscriber_port = None
    __kafka_producer_port = None
    
    def load_config():
        pass

class RequestProducer(kafkaClient):
    
    __instance = None
    
    def __init__(self):
        #bootstrap_server = "remote_host:port"
        self.producer = KafkaProducer(bootstrap_servers = "dimitris-VirtualBox:9092")
        RequestProducer.__instance = self
        
        
    @staticmethod
    def GetInstance():
        return RequestProducer.__instance
    
    
    def SendRequest(self, topic: str, dataframe: DataFrame):
        for row in dataframe.iterrows():
            self.producer.send(topic, str(row).encode('utf-8'))
            
            
class Consumer(kafkaClient):
    pass