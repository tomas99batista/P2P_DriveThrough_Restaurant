# coding: utf-8

import time
import pickle
import socket
import random
import logging
import argparse
import threading
from node import Node
from utils import work

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S')
logger = logging.getLogger('Restaurant')

class Restaurant(threading.Thread):
    def __init__(self, port=5000, ide=0):
        threading.Thread.__init__(self) #Inicia thread de trabalho
        self.comm_object = Node('Restaurant', 0, ('localhost', 5000), 4)        
        self.id = ide
        self.port = port

    def run(self):
        self.comm_object.start()
        #self.Logger.info('Starting Restaurant')
        
        while True:
            while True:
                if self.comm_object.out_queue.qsize != 0:
                    break
                work(5)      
            o = self.comm_object.out_queue.get()

#TODO: adicionar tempos de espera

            self.comm_object.logger.info('Restaurant Received ORDER to COOK: %s ', o['args'])
            self.Grill_quantity = o['args']['order']['hamburger']
            self.Fries_quantity = o['args']['order']['fries']
            self.Drinks_quantity = o['args']['order']['drink']
            # Griller
            if self.Grill_quantity != 0:
                self.comm_object.logger.info('Grilling %s hamburgers', self.Grill_quantity)
                for i in range(self.Grill_quantity):
                    time.sleep(random.gauss(3, 0.5))
            # Fries
            if self.Fries_quantity != 0:
                self.comm_object.logger.info('Frying %s fries', self.Fries_quantity)
                for i in range(self.Fries_quantity):
                    time.sleep(random.gauss(5, 0.5))
            # Drinks
            if self.Drinks_quantity != 0:
                self.comm_object.logger.info('Serving %s drinks', self.Drinks_quantity)
                for i in range(self.Drinks_quantity):
                    time.sleep(random.gauss(1, 0.5))
            o = {'method': 'COOKEED_ORDER', 'args': o['args'] }
            self.comm_object.send(self.comm_object.successor_addr, o)
            self.comm_object.logger.info('Restaurant Sent COOKED ORDER no %s', o['args'])