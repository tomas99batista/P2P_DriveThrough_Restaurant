# coding: utf-8

import time
import pickle
import socket
import random
import logging
import argparse
import threading
import uuid
from node import Node
from utils import work


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S')
logger = logging.getLogger('Waiter')


class Waiter(threading.Thread):
    def __init__(self, port=5001, ide=1):
        threading.Thread.__init__(self)
        self.comm_object = Node('Waiter', 1, ('localhost', 5001), 4, ('localhost', 5000))
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

            self.comm_object.logger.info('Waiter Received ORDER: %s ', o['args'])
            
            order_id = uuid.uuid4()
            order = o['args']

            # Envia para o sucessor a order c/ ID e quantidades pedidas
            o = {'method': 'SEND_ORDER', 'args': {'order_ID' : order_id , 'order' :  order } }
            self.comm_object.send(self.comm_object.successor_addr, o)
            self.comm_object.logger.info('Waiter Sent ORDER no %s, %s',order_id, order)

            # Envia para o restaurante para devolver o Order_ID ao cliente
            o = {'method' : 'NOTE_ORDER' , 'args' : order_id }
            self.comm_object.send(self.comm_object.restAddr , o )
            self.comm_object.logger.info('Waiter sent Ticket number %s to preare: %s', order_id, order)
