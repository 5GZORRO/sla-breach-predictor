# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 12:22:37 2021

@author: dlaskaratos
"""


class AttributeListCannotBeEmptyException(Exception):
    
    def __init__(self, reason = "The list of attributes for model training cannot be empty."):
        self.reason = reason
        super().__init__(self.reason)
        

class PathNotFoundException(Exception):
    
    def __init__(self, path: str):
        self.reason = "Path '"+path+"' was not found."
        super().__init__(self.reason)


class OperationNotRegisteredException(Exception):
    
    def __init__(self, operation_id: str):
        self.reason = "Operation '"+operation_id+"' was not found in the registry."
        super().__init__(self.reason)