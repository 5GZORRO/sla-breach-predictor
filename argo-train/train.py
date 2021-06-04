# -*- coding: utf-8 -*-
"""
Created on Wed May 19 11:26:09 2021

@author: dlaskaratos
"""

import os
from os import path
from keras.models import load_model
import pandas as pd
import numpy as np

def split_sequence(sequence, n_steps):
        
        X, y = list(), list()
        for i in range(len(sequence)):
            end_ix = i + n_steps
            if end_ix > len(sequence)-1:
                break
            seq_x, seq_y = sequence[i:end_ix], sequence[end_ix:end_ix+1]
            X.append(seq_x)
            y.append(seq_y)
        return np.array(X), np.array(y)

print('Loading model..')

model = load_model('/isbp-data/saved/lstm')
data = pd.read_csv('/isbp-data/train.csv')
data = data['bw'].to_numpy().tolist()
X, y = split_sequence(data, 3)
X = X.reshape((X.shape[0], X.shape[1], 1))
model.fit(X, y, epochs=200, verbose=0)
print('Training completed')
os.remove('/isbp-data/train.csv')
if not path.exists('/isbp-data/train.csv'):
    print('File successfully removed')