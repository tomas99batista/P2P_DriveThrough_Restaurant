# coding: utf-8

import time
import pickle
import socket
import random
import logging
import argparse
import threading
from utils import *
from node import Node


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S')
logger = logging.getLogger('Chef')


class Chef(threading.Thread):
    def __init__(self, port=5002, ide=2):
        threading.Thread.__init__(self)
        self.comm_object = Node('Chef', 2, ('localhost', 5002), 4, ('localhost', 5000))
        self.id = ide
        self.port = port
    
    def run(self):
        self.comm_object.start()
#TODO: adicionar tempos de espera
        while True:
            while True:
                if self.comm_object.out_queue.qsize != 0:
                    break
                work(5)      
            o = self.comm_object.out_queue.get()
            if o['method'] == 'SEND_ORDER':
                self.comm_object.logger.info('Chef received ORDER to PREPARE: %s ', o['args'])
                o = {'method': 'PREPARE_ORDER', 'args' : o['args']}
                self.comm_object.send(self.comm_object.restAddr, o)
                self.comm_object.logger.info('Chef Sent PREPARE ORDER no %s', o['args'])
            elif o['method'] == 'COOKEED_ORDER':
                o = {'method' : 'DISPATCH_ORDER' , 'args' : o['args'] }
                self.comm_object.send(self.comm_object.successor_addr , o )
                self.comm_object.logger.info('Chef Sent DISPATCHED ORDER: %s', o['args'])

