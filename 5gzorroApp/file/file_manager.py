# -*- coding: utf-8 -*-
"""
Created on Wed Feb 24 14:16:17 2021

@author: dlaskaratos
"""

from pathlib import Path

class FileManager():
    
    def create_path_if_not_exists(_path) -> Path:
        if not Path(_path).exists():
            Path(_path).mkdir(parents = True, exist_ok = True)
            path = Path(_path)
        else:
            path = Path(_path)
        
        return path
    
    def path_exists(_path):
        if Path(_path).exists():
            return True
        else:
            return False
    