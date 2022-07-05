# -*- coding: utf-8 -*-
"""
Created on Thu May 12 10:21:38 2022

@author: dlaskaratos
"""

from abc import ABC, abstractmethod,abstractproperty
import numpy as np
import pandas as pd
from pickle import load
from tensorflow import keras
from joblib import load
from darts import TimeSeries

class Model(ABC):
    
    def __init__(self):
        super().__init__()
        self.model = None
        self.name = None
        self.extension = ''
        
    @abstractmethod
    def save(self, path):
        pass
    
    @abstractmethod
    def load(self, path):
        pass
    
    @abstractmethod
    def predict(self, values):
        pass
    
    @abstractmethod
    def train(self, dataset):
        pass
    
class LSTM(Model):
    
    
    def __init__(self):
        super().__init__()
        
    def save(path):
        pass
    
    def load(self, path):
    
        self.model = keras.models.load_model(path+'/'+self.name)
    
    def predict(self, values):
        X = np.array([values])
        inp = X.reshape((X.shape[0], X.shape[1], 1))
        yhat = self.model.predict(inp, verbose=0)
        prediction = yhat[0][0]
        return prediction
    
    def train(self, dataset):
        pass
        
    def _print(self):
        print(self.model)

class SVR(Model):
    
    def __init__(self):
        super().__init__()
        self.extension = '.joblib'
        
    def save(path):
        pass
    
    def load(self, path):
        from joblib import load
        self.model = load(path+'/'+self.name+self.extension)
        
    def predict(self, values):
        X = np.array([values])
        inp = X = X.reshape((X.shape[0], X.shape[1]))
        yhat = self.model.predict(inp)
        prediction= yhat[0]
        return prediction
    
    def train(self, dataset):
        pass
        # from sklearn.svm import SVR
        # from joblib import dump, load
        
        # X = dataset.reshape((X.shape[0], X.shape[1]))
        # model.fit(X, y)
        # dump(model, path_to_model+'/'+model_id+'.joblib')
        # with ZipFile(zip_model, 'w') as zipObj:
        #     zipObj.write(path_to_model+'/'+model_id+'.joblib')
        # success = True
    
    def _print(self):
        print(self.model)
        
class NBeats(Model):
    
    def __init__(self):
        super().__init__()
        self.extension = '.pth.tar'
        
    def save(self, path):
        pass
    
    def load(self, path):
        from darts.models.forecasting.nbeats import NBEATSModel
        self.model = NBEATSModel.load_model(path+'/'+self.name+self.extension)
        
    
    def predict(self, values):
        
        r = np.array(values)
        series = TimeSeries.from_values(r).astype(np.float32)
        transformer = load(open("/data/models/nbeats_scaler.pkl", "rb"))
        values_scaled = transformer.transform(series)
        prediction = self.model.predict(series = values_scaled,
                                          n = 1, 
                                          # n_jobs = -1, # set this to utulize all threads (might not be needed for ISBP)
                                          verbose = False
                                          )
        pred_val = prediction.univariate_values()[0]
    # Unscale
        pred_val = pred_val.reshape(-1, 1)
        pred_val = TimeSeries.from_values(pred_val).astype(np.float32)
        pred_val = transformer.inverse_transform(pred_val)
        return pred_val.first_value()
        # return pred_val
    
    def train(self, dataset):
        pass
        