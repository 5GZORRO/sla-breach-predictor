# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 10:06:54 2021

@author: Dimitris
"""

from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError, NoBrokersAvailable
import logging
from config.config import Config as cnf


class Consumer():
    
    def __init__(self):
        # self.topics = topics
        try:
            host = cnf.KAFKA_HOST
            port = cnf.KAFKA_PORT
            data_topic = cnf.MON_TOPIC
            self.consumer = KafkaConsumer(data_topic, bootstrap_servers = host+ ":"+ port)
        except NoBrokersAvailable as nba:
            logging.info(str(nba))
            
    
    def subscribe(self, topics):
        self.consumer.assign(topics)
    
    def get(self, max_records):
        data = self.consumer.poll(timeout_ms = cnf.KAFKA_POLL_TIMEOUT, max_records = max_records)
        return data
        
        
    def get_or_resubscribe(self):
        topics = self.consumer.assignment()
        if not topics: # Consumer has not subscribed to any topics yet
            try:
                self.consumer.subscribe(self.topics)
            except KafkaError as ke:
                logging.info("Error while trying to subscribe to topics: %s", ke)
        else:
            try:
                self.consumer.unsubscribe()
                self.consumer.subscribe(topics)
            except KafkaError as ke:
                logging.info("Error while unsubscribing: %s", ke)
        for msg in self.consumer:
            logging.info(msg.value)
    
    def set_topics(self, new_topics):
        self.topics.append(new_topics)
        

class Producer():
    
    producer = None
    
    def init():
        global producer
        host = cnf.KAFKA_HOST
        port = cnf.KAFKA_PORT
        try:
            producer = KafkaProducer(bootstrap_servers = host+ ":"+ port)
        except NoBrokersAvailable as nba:
            logging.info(str(nba))
    
    def send(data):
        global producer
        producer.send(cnf.BREACH_TOPIC, data.encode('utf-8'))
            