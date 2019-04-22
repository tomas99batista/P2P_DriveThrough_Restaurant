# coding: utf-8

import time
import pickle
import socket
import random
import logging
import argparse
import threading
from node import Node
from utils import *
import uuid


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S')
logger = logging.getLogger('Clerk')


class Clerk(threading.Thread):
    def __init__(self, port=5003, ide=3):
        threading.Thread.__init__(self)
        self.comm_object = Node('Clerk', 3, ('localhost', 5003), 4, ('localhost', 5000))
        self.id = ide
        self.port = port

    def run(self):
        self.comm_object.start()

#TODO: adicionar tempos de espera

        while True:
            while True:
                if self.comm_object.out_queue.qsize != 0:
                    break
                work(15)      
            
            self.pedidos = {}
            
            o = self.comm_object.out_queue.get()
            self.comm_object.logger.info('Clerk Received ORDER to DISPATCH: %s ', o['args'])
            self.order_id = o['args']
            args = o['args']
            
            if o['method'] == 'DISPATCH_ORDER':
                o = {'method': 'DELIVER_ORDER', 'args' : args} 
                self.comm_object.send(self.comm_object.restAddr, o)
                self.comm_object.logger.info('Clerk DELIVER_ORDER no %s: %s', self.order_id, args)
            #TODO: CODE FOR 2 CLIENTS:
            
            '''
            # Client asking to pick food
            if o['method'] == 'PICKUP':
                while self.order_id not in self.pedidos:
                    self.comm_object.logger.info("Client wants to pick %s: ", self.order_id)
                    work(5)
                order = self.pedidos.pop(self.order_id)
                o = {'method': 'DELIVER_ORDER', 'args' : args} 
                self.comm_object.send(self.comm_object.restAddr, o)
                self.comm_object.logger.info('Clerk DELIVER_ORDER no %s: %s', self.order_id, args)
            # Chef sending food to the client
            elif o['method'] == 'DISPATCH_ORDER':
                #self.comm_object.logger.info("TOU AQUI")
                #elf.pedidos[self.order_id] = o['args']  # TODO: Problemas com indexar ID
                self.comm_object.logger.info('Clerk Added to waiting dispatch orders order no %s: %s', self.order_id, args)
                '''