# -*- coding: utf-8 -*-
"""
Created on Wed Dec 23 15:27:41 2020

@author: dlaskaratos ICOM
"""

from algorithms.models import ModelEntity, BaseLSTM, BaseARIMA, UnivariateLSTM
from keras.models import load_model
from config.config import Config as cnf
from file.file_manager import FileManager as fm
from algorithms.model_descriptor import ModelDescriptor as md
from datetime import datetime
import logging


log = logging.getLogger(__name__)

class ModelManager():
    
    __base_algorithms = None
    
    def init() -> None:
        global __base_algorithms
        __base_algorithms = {}
        __base_algorithms['lstm'] = BaseLSTM
        __base_algorithms['arima'] = BaseARIMA
        
    
    def construct_model_entity(pipeline_id, rule) -> ModelEntity:
       global __base_algorithms
       md.register_pipeline(pipeline_id)
       metric = rule.get('metric')
       threshold = rule.get('tolerance')
       model_data = rule.get('model_data')
       if model_data is not None:
           base = model_data.get('base')
           model_entity = __base_algorithms.get(base).get_specification(model_data)
       else:
           model_entity = UnivariateLSTM(model_data)
       model_entity.id = model_entity.base +'-'+ model_entity.name +'-'+str(model_entity.n_steps)+'-'+str(model_entity.out)
       model_entity.metric = metric
       model_entity.threshold = threshold
       return model_entity
   
    def save_model(pipeline_id, model_entity: ModelEntity):
        model_id = model_entity.id
        path = cnf.SAVE
        path = fm.create_path_if_not_exists(path+'/'+str(pipeline_id)+'/'+model_id)
        date = datetime.now().strftime("%d-%m-%Y_%H-%M")
        version = date
        model_entity.model.save(path/version)
        md.register_model(pipeline_id, model_id, path, version, {'accuracy': 0})
            
        
    def load_model(pipeline_id, model_id):
        model = None
        result = None
        try:
           version = md.get_version_path(pipeline_id, model_id)
           model = load_model(version)
           result = 'Model sucessfully loaded'
        except Exception as ex:
                result = str(ex)
        return result, model