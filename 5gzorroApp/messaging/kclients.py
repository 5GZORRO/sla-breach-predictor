# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 10:06:54 2021

@author: Dimitris
"""

from kafka import KafkaConsumer, KafkaProducer, TopicPartition
from kafka.errors import NoBrokersAvailable
import logging
from config.config import Config as cnf


class Consumer():
    
    def __init__(self):
        self.topic = None
        self.partition = None
        try:
            host = cnf.KAFKA_HOST
            port = cnf.KAFKA_PORT
            self.consumer = KafkaConsumer(group_id = 'sla-breach-predictor', bootstrap_servers = host+ ":"+ port)
        except NoBrokersAvailable as nba:
            logging.info(str(nba))
            
    
    def subscribe(self, topic):
        self.topic = topic
        self.partition = TopicPartition(self.topic, 0)
        self.consumer.assign([self.partition])
    
    def get_records(self, max_records):
        data = self.consumer.poll(timeout_ms = cnf.KAFKA_POLL_TIMEOUT, max_records = max_records)
        return data        

class Producer():
    
    producer = None
    
    def init():
        global producer
        host = cnf.KAFKA_HOST
        port = cnf.KAFKA_PORT
        producer = KafkaProducer(bootstrap_servers = host+ ":"+ port)
    
    def send(data):
        global producer
        producer.send(cnf.BREACH_TOPIC, data.encode('utf-8'))
            