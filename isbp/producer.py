from kafka import KafkaProducer
import json
import pandas as pd
import numpy as np
from datetime import datetime
import time

producer = KafkaProducer(bootstrap_servers = '172.28.3.196:9092')

data = pd.read_csv('dataset.csv')
srv = data[0:3]

for index, row in srv.iterrows():
    timestamp = row['unix-timestamp']
    value = row['availability-percent']
    monitoring_data = {
            "resourceID": "isbp",
            "referenceID": "isbp",
            "transactionID": "tran1",
            "productID": "isbp",
            "instanceID": "inst1",
            "metricName": "metric1",
            "metricValue": value,
            "timestamp": str(timestamp)
            }
    postMonitoringDataDict = {
            "operatorID": 'isbp',
            "businessID": 'isbp',
            "networkID": 'isbp',
            "MonitoringData": monitoring_data,
            }

    msg = json.dumps(postMonitoringDataDict) 
    producer.send('isbp-in-0', msg.encode('utf-8'))
    producer.flush()
    time.sleep(40)
