# -*- coding: utf-8 -*-
"""
Created on Wed Jun 16 17:01:38 2021

@author: dlaskaratos
"""

from kafka import KafkaProducer
import json
import pandas as pd
import numpy as np
from datetime import datetime
import time


producer = KafkaProducer(bootstrap_servers = '172.28.3.196:9092')
sla = {"data": {"eventType": "new_SLA", 
                "transactionID": "fe41aa60d4594ca886c93992445d95f9", 
                "productID": "isbp", 
                "resourceID": "789", 
                "instanceID": "10", 
                "kafka_ip": "localhost", 
                "kafka_port": "9092", 
                "topic": "isbp-topic-out"}}


msg = json.dumps(sla)
producer.send('isbp-topic', msg.encode('utf-8'))
producer.flush()