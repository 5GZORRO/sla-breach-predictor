# -*- coding: utf-8 -*-
"""
Created on Tue Sep  6 15:09:08 2022

@author: dlaskaratos
"""
import os
from os import path
from predict import copy_model
import shutil


def create_transaction_folder(data):
    
    transactionid = data.get('transactionid').replace(":", "-")
    name = data.get('name')
    _class = data.get("class")
    if path.exists("/data/models"):
        new_folder = '/data/models/'+transactionid
        os.makedirs(new_folder, exist_ok=True)
        copy_model(transactionid, new_folder, name, _class)

def delete_transaction_folder(transactionid: str):
    result = None
    transactionID = transactionid.replace(":", "-")
    if path.exists("/data/models/"+transactionID):
        shutil.rmtree('/data/models/'+transactionID)
        result = 'Folder ./{0} has been deleted.'.format(transactionID)
    else:
        result = 'Folder ./{0} not found.'.format(transactionID)
    return result
    
def remove_model_from_folder():
    pass