# -*- coding: utf-8 -*-
"""
Created on Thu Dec 24 14:29:41 2020

@author: dlaskaratos ICOM
"""

from algorithms.model_manager import ModelManager as manager
from messaging.kclients import Consumer, Producer
import logging
from config.config import Config as cnf
import threading
import time
import json
from exceptions.exceptions import MetricNotFoundException
from datetime import datetime

class ActivePipeline():
    
    def __init__(self, _id, name, description, rules) -> None:
        self.id = int(_id)
        self.name = name
        self.description = description
        self.models = self.__extract_rules__(self.id, rules)
        
######### ONLY FOR TESTING PURPOSES ########
        
    def train(self):
        self.__active_training = True
        self.__model_entity.train(None, None)
        manager.save(self.__model_entity)
    
    def predict(self):
        model = self.models.get('lstm-univariate-3-1')
        load_result, saved_model = manager.load_model(self.id, model.id)
        # print(load_result)
        model.set_model(saved_model)
        model.predict()
        
############################################
    
    def start_training(self, model_entity):
        logging.info('Started thread with id: %s', threading.current_thread().ident)
        # consumer = Consumer()
        # consumer.subscribe(cnf.MON_TOPIC)
        model_entity.active_training = True
        
        while(model_entity.active_training):
            
            try:
                # dataset = list()
                # msg_pack = consumer.get_records(5)
                # for tp, messages in msg_pack.items():
                #     for message in messages:
                #         dct = message.value.decode('utf-8')
                #         data = json.loads(dct)
                #         metric = data[model_entity.metric]
                #         dataset.append(float(metric))
                model_entity.train()
                manager.save_model(self.id, model_entity)
                model_entity.model_available = True
                model_entity.new_model = True
                model_entity.active_training = False
                result = "Model successfully saved"
            except Exception as ex:
                result = "Error during model training or saving: " + str(ex)
                
            logging.info(result)
        
            time.sleep(cnf.TR_TMT)
        
        logging.info("Training concluded...")
        
    def start_predicting(self, model_entity):
        counter = 0
        _round = 0
        model_entity.active_prediction = True
        consumer = Consumer()
        consumer.subscribe(cnf.MON_TOPIC)
        
        while(not model_entity.model_available):
            counter += 1
            logging.info('WAITING FOR A MODEL TO BE AVAILABLE... %s', counter)
            time.sleep(cnf.W_TMT)
        
        logging.info('STARTING PREDICTION CYCLE')
        
        metrics = list()
        dates = list()
        
        while(model_entity.active_prediction):
            _round += 1
            if(model_entity.new_model):
                load_result, saved_model = manager.load_model(self.id, model_entity.get_id())
                if saved_model != None:
                    model_entity.set_model(saved_model)
                    model_entity.new_model = False
                else:
                    logging.error("Could not load new model. %s", load_result)
            
            try:
                for message in consumer.consumer:
                    dct = message.value.decode('utf-8')
                    data = json.loads(dct)
                    #     result_array = data.get('data').get('result')
                    #     for item in result_array:
                    #         metric = item.get('metric')
                    #         if metric is not None:
                    #             name = metric.get('__name__')
                    #             if name != model_entity.metric:
                    #                 continue
                    #             else:
                    #                 value = item.get('value')
                    #                 dates.append(value[0])
                    #                 metrics.append(float(value[1]))
                    dates.append(data['time'])
                    metric = data[model_entity.metric]
                    if metric is not None:
                        metrics.append(float(metric))
                    else:
                        raise MetricNotFoundException(model_entity.metric)
                    if len(metrics) < model_entity.n_steps:
                        continue
                    else:
                        prediction = model_entity.predict(metrics)
                        metrics.pop(0)
                        if prediction > model_entity.threshold:
                            timestamp = str(dates[len(dates)-1])[:-5]
                            timestamp = int(timestamp)+60
                            date = datetime.fromtimestamp(timestamp)
                            notification = 'Predicted violation of threshold '+str(model_entity.threshold)+' with value: '+str(prediction)+ ' at '+str(date)
                            Producer.send(notification)
            except Exception as e:
                logging.error('Error during prediction process: %s', str(e))
            
            # time.sleep(cnf.PRD_TMT)
        
        logging.info('PREDICTION CYCLE ENDED')
        
    def update_model(self, model_data):
        logging.info('Terminating current running operations...')
        try:
            self.terminate_operations(clean_up = False)
            logging.info('Constructing new model...')
            self.__model_entity = manager.construct_model_entity(model_data)
            result = 'Model successfully updated.'
            logging.info(result)
        except Exception as e:
            result = 'Failed to update model: ', str(e)
        
        return result
                
           
    def write_values_to_log(self, entity, _list, _round):
        logs_path = cnf.LOGS
        try:
            file = open(logs_path+entity.get_id()+str(_round)+".log", "a+")
            for line in _list:
                file.write(str(line)+"\n")
        except Exception as ex:
            logging.error(str(ex))
        
    def __extract_rules__(self, pipeline_id, rules):
        models = {}
        for rule in rules:
            model_entity = manager.construct_model_entity(pipeline_id, rule)
            models[model_entity.id] = model_entity
        return models
