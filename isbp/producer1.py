# -*- coding: utf-8 -*-
"""
Created on Thu Oct 14 13:09:20 2021

@author: dlaskaratos
"""

from kafka import KafkaProducer
import json
import pandas as pd
import numpy as np
from datetime import datetime
import time

producer = KafkaProducer(bootstrap_servers = '172.28.3.196:9092')

data = {
    "data": {
        "eventType": "new_SLA",
        "transactionID": "e2e2ecaeec944aa793ff701e667c1908",
        "productID": "2",
        "resourceID": "250f91b5-a42b-46a5-94cd-419b1f3aa9e0",
        "instanceID": "52",
        "kafka_ip": "172.28.3.196",
        "kafka_port": "9092",
        "topic": "isbp-topic"}
}
msg = json.dumps(data)
producer.send('isbp-topic', msg.encode('utf-8'))
producer.flush()

data = {
    "data": {
        "eventType": "new_SLA",
        "transactionID": "e2e2ecaeec944aa793ff701e667c1908",
        "productID": "1",
        "resourceID": "250f91b5-a42b-46a5-94cd-419b1f3aa9e0",
        "instanceID": "52",
        "kafka_ip": "172.28.3.196",
        "kafka_port": "9092",
        "topic": "isbp-topic"}
}
msg = json.dumps(data)
producer.send('isbp-topic', msg.encode('utf-8'))
producer.flush()