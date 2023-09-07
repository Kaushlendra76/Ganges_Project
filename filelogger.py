
#   Copyright 2018-2019 AyKa Technologies
#

import logging
import Global
from configparser import *

# Open serial port
class DataLogger(object):
    def __init__(self):
    
        #global logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # create a file handler
        self.handler = logging.FileHandler('debug.log')
        self.handler.setLevel(logging.INFO)
        
        # create a logging format
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.handler.setFormatter(self.formatter)
        
        # add the handlers to the logger
        self.logger.addHandler(self.handler)
    
    def message(self,msg):
        self.logger.info(msg)
        

