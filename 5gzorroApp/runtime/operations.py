# -*- coding: utf-8 -*-
"""
Created on Thu Feb 25 09:58:05 2021

@author: dlaskaratos
"""

from algorithms.model_manager import ModelManager as manager
import threading
from config.config import Config as cnf
import time
import logging

class TrainOperation(threading.Thread):
        
    def run(self, execution):
        print('Started thread with id: ', threading.current_thread().ident)
        TR_TMT = int(cnf.TR_TMT)
        counter = 0
        while(execution.is_active_training()):
            counter = counter + 1
            logging.info("Training round: %s", counter)
            try:
                execution.get_model_entity().train()
                # manager.save(entity)
                execution.set_model_available(True)
                execution.set_new_model(True)
                result = "Model successfully saved"
            except Exception as ex:
                result = "Error during model training or saving: " + str(ex)
        
            logging.info(result)
            time.sleep(TR_TMT)
        
        logging.info("Training concluded...")


class PredictOperation(threading.Thread):
    
    def run(self, execution):
        entity = execution.get_model_entity()
        W_TMT = int(cnf.W_TMT)
        PRD_TMT = int(cnf.PRD_TMT)
        counter = 0
        num = 0
        
        while(not execution.is_model_available()):
            counter = counter + 1
            print('WAITING FOR A MODEL TO BE AVAILABLE... ', counter)
            time.sleep(W_TMT)
        
        print('STARTING PREDICTION CYCLE')
        
        while(execution.is_active_prediction()):
            num = num + 1
            print('Prediction No. ', num)
            if(execution.is_new_model()):
                load_result, saved_model = manager.load(entity.get_id())
                if saved_model != None:
                    entity.set_model(saved_model)
                    execution.set_new_model(False)
                else:
                    logging.error("Could not load new model. %s", load_result)
            
            try:
                exceed_list = entity.predict()
                # self.write_values_to_log(entity, exceed_list, _round)
            except Exception as ex:
                logging.error("Error during prediction process. %s", str(ex))
            
            time.sleep(PRD_TMT)
        
        print('PREDICTION CYCLE ENDED')