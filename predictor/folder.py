# -*- coding: utf-8 -*-
"""
Created on Tue Sep  6 15:09:08 2022

@author: dlaskaratos
"""
import os
from os import path
from predict import copy_models


def create_transaction_folder(data):
    
    transactionid = data.get('transactionid').replace(":", "-")
    models = data.get('models')
    if path.exists("/data/models"):
        new_folder = '/data/models/'+transactionid
        os.makedirs(new_folder, exist_ok=True)
        copy_models(transactionid, new_folder, models)

def delete_transaction_folder(transactionid: str):
    pass
    
def remove_model_from_folder():
    pass