# -*- coding: utf-8 -*-
"""
Created on Wed Dec 23 15:27:41 2020

@author: Dimitris
"""

from __future__ import annotations
from algorithms.models import Model, BaseLSTM, BaseARIMA
from keras.models import load_model


class ModelLoader():
    
    __instance = None
    
    def __init__(self) -> None:
        self.base_algorithms = {}
        self.base_algorithms['lstm'] = BaseLSTM
        self.base_algorithms['arima'] = BaseARIMA
        ModelLoader.__instance = self
        
    @staticmethod
    def get_instance():
        return ModelLoader.__instance
        
    
    def get_model(self, model_data) -> Model:
       algorithm = self.base_algorithms.get(model_data.get('base')).get_specification(model_data.get('spec'))
       return algorithm
   
    def save(self, model: Model):
        model.get_model().save("result")
        
    def load(self):
        model = load_model("result")
        return model