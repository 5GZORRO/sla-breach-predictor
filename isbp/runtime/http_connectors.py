# Helper methods that perform HTTP requests to 5GZORRO modules to retrieve or post information

from config.config import Config as cnf
import requests
import json
import logging

log = logging.getLogger(__name__)
params = {'userId' : 'isbp', 'authToken' : 'blah'}

def register_app():

    global params
    datalake_ip = cnf.DATALAKE
    register_url = 'http://'+datalake_ip+'/datalake/v1/user'
    status = None
    
    try:
        request = requests.post(register_url, json = params)
        if request.status_code == 409:
            log.info('App already registered.Getting information.')
            request = requests.get(register_url, json = params)
        response = json.loads(request.text)
        data_topic = response.get('availableResources').get('topics').get('userInTopic')
        kafka_url = response.get('availableResources').get('urls').get('kafka_url').split(':')
        cnf.TOPICS.append(data_topic)
        cnf.KAFKA_HOST = kafka_url[0]
        cnf.KAFKA_PORT = kafka_url[1]
        cnf.MON_DATA_TOPIC = data_topic
        cnf.DATALAKE_STREAM = response.get('availableResources').get('urls').get('dl_stream_data_server_url')
        status = request.status_code
    except Exception as e:
        log.error(e)
        status = -1
    
    return status
    

def register_pipeline(transactionID):
    global params
    stream_url = cnf.DATALAKE_STREAM
    register_url = 'http://'+stream_url+'/datalake/v1/stream_data/register/'+transactionID
    
    token = {'userInfo' : params, 'productInfo' : {'topic' : cnf.MON_DATA_TOPIC}}
    request = requests.post(register_url, json = token)
    if request.status_code > 200 and request.status_code < 300:
        log.info("Successfully registered pipeline with Product ID: {0}".format(transactionID))
    else:
        log.info("Registration failed.")
        
    

def get_sla_details(slaID):
    lcm_ip = cnf.LCM
    sla_url = 'http://'+lcm_ip+'/smart-contract-lifecycle-manager/api/v1/service-level-agreement/'
    response = None
    request = requests.get(sla_url+slaID)
    log.info('SLA status: {0}'.format(request.status_code))
    if request.status_code == 200:
        response = json.loads(request.text)
        result = 'SLA details successfully retrieved'
    else:
        result = 'SLA not found or could not be retrieved'
    
    return response, result