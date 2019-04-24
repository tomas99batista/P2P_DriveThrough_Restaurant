# TODO: Tabela de entidades, uar dicionario {'nome': [0,1]} => Usar lista pq podemos ter 2 cozinheiros

# coding: utf-8

import socket
import threading
import logging
import pickle
from utils import contains_successor
from queue import Queue

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S')
logger = logging.getLogger('node')

class Node(threading.Thread):
    def __init__(self, Name, ide, address, sizeRing = 4, restAddress = None, timeout=3):
        threading.Thread.__init__(self)
        self.name = Name
        self.id = ide
        self.addr = address
        self.ring_size = sizeRing
        self.restAddr = restAddress
        self.out_queue = Queue()    # Queue to get things from communication thread -> work thread
        #self.messageCount = 0
        #self.fileName = "file_" + self.name + ".txt"
        #self.file = open(self.fileName, "w+")
        
        # Se o restAddress é null é porque é o restaurant e faz ring c/ ele próprio
        if restAddress is None:
            self.successor_id = self.id
            self.successor_addr = self.addr
            self.inside_dht = True
        else:
            self.inside_dht = False
            self.successor_id = None
            self.successor_addr = None
        
        # tabela de entidades
        self.table = {self.name: self.id}
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(timeout)
        self.logger = logging.getLogger("Node {}".format(self.id))
    
    # Tablela c/ as infos de todas as entidades
    def get_table(self):
      return self.table

    def node_join(self, args):
        self.logger.debug('Node join: %s', args)        
        addr = args['addr']
        identification = args['id']   
        if self.id == self.successor_id:
            self.successor_id = identification
            self.successor_addr = addr
            args = {'successor_id': self.id, 'successor_addr': self.addr}
            self.send(addr, {'method': 'JOIN_REP', 'args': args})
        elif contains_successor(self.id, self.successor_id, identification):
            args = {'successor_id': self.successor_id, 'successor_addr': self.successor_addr, 'rest_addr' : self.restAddr}
            self.successor_id = identification
            self.successor_addr = addr
            self.send(addr, {'method': 'JOIN_REP', 'args': args})
        else:
            self.logger.debug('Find Successor(id: %d)', args['id'])
            self.send(self.successor_addr, {'method': 'JOIN_REQ', 'args':args})
        self.logger.info(self)

    def node_discovery(self, name, ide, table, count):
        if name not in table.keys():
            table[name] = ide
        self.table = table
        o = {'method': 'NODE_DISCOVERY', 'args': {'table': self.table, 'round':count}}
        self.send(self.successor_addr, o)
        
    def run(self):
        self.socket.bind(self.addr)
        while not self.inside_dht:
            o = {'method': 'JOIN_REQ', 'args': {'addr': self.addr, 'id':self.id}}
            self.send(self.restAddr, o)
            p, addr = self.recv()
            if p is not None:
                o = pickle.loads(p)
                if o['method'] == 'JOIN_REP':
                    args = o['args']
                    self.successor_id = args['successor_id']
                    self.successor_addr = args['successor_addr']
                    self.inside_dht = True
                    self.logger.info(self)     
        # Start Sending Ring Count
        if self.id == 0:
            o = {'method': 'RING_COUNT', 'args': { 'count': 1 }}
            self.send(self.successor_addr, o)
        done = False
        while not done:
            p, addr = self.recv()
            if p is not None:
                o = pickle.loads(p)
                self.logger.debug('O: %s', o)
                # ------RING_COUNT------
                if o['method'] == 'RING_COUNT':
                    if self.id == 0:    # Se estivermos no restaurant
                        if o['args']['count'] == self.ring_size: # 4, todas as entidades ligadas => Start NODE_DISCOVERY
                            o = {'method': 'NODE_DISCOVERY', 'args': {'table': self.table, 'round' : 1}}
                            self.send(self.successor_addr, o)
                        else:   # Nem todas se conhecem
                            o['args']['count'] = 1 # Reset count
                    else:   # Se não estivermos no restaurante -> incrementa
                        o['args']['count'] += 1
                    self.send(self.successor_addr, o)
                # ------JOIN_REQ------
                elif o['method'] == 'JOIN_REQ':
                    self.node_join(o['args'])
                # ------NODE_DISCOVERY------
                elif o['method'] == "NODE_DISCOVERY":
                    ronda = o['args']['round']
                    if ronda < 3 :
                        if self.id == 0:
                            ronda += 1
                        self.node_discovery(self.name, self.id, o['args']['table'], ronda)  
                # --------------------MÉTODOS ENTIDADES--------------------                    
                    # CLIENT METHODS
                elif o['method'] == 'ORDER':
                    if self.id == self.table.get('Waiter'):
                        self.out_queue.put(o)
                    else:
                        self.send(self.successor_addr, o)
                elif o['method'] == 'PICKUP':
                    if self.id == self.table.get('Clerk'):
                        self.out_queue.put(o)
                    else:
                        self.send(self.successor_addr, o)                  
                    
                    # WAITER METHODS
                elif o['method'] == 'NOTE_ORDER':
                    if self.id == self.table.get('Restaurant'):
                        self.send(('localhost' , 5004) ,o) 
                    else:
                       self.send(self.successor_addr, o)
                elif o['method'] == 'SEND_ORDER':
                    if self.id == self.table.get('Chef'):
                        self.out_queue.put(o)
                    else:
                       self.send(self.successor_addr, o)

                    # CHEF METHODS
                elif o['method'] == 'PREPARE_ORDER':
                    if self.id == self.table.get('Restaurant'):
                        self.out_queue.put(o)
                    else:
                        self.send(self.successor_addr, o)
                elif o['method'] == 'COOKEED_ORDER':
                    if self.id == self.table.get('Chef'):
                        self.out_queue.put(o)
                    else:
                        self.send(self.successor_addr, o)
                elif o['method'] == 'DISPATCH_ORDER':
                    if self.id == self.table.get('Clerk'):
                        self.out_queue.put(o)
                    else:
                        self.send(self.successor_addr, o)
                
                    # CLERK METHODS
                elif o['method'] == 'DELIVER_ORDER':
                    if self.id == self.table.get('Restaurant'):
                        self.logger.info('---> DELIVERED order: %s', o['args'])
                        self.send(('localhost', 5004), o) # TODO: ver como obter a porta do cliente pq podemos ter múltiplos
                    else:
                        self.send(self.successor_addr, o)

    def send(self, address, o):
            p = pickle.dumps(o)
            self.socket.sendto(p, address)

    def recv(self):
        try:
            p, addr = self.socket.recvfrom(1024)
        except socket.timeout:
            return None, None
        else:
            if len(p) == 0:
                return None, addr
            else:
                return p, addr

    def __str__(self):
        return 'Name: {}; Node ID: {}; Inside: {}; Successor: {}'\
            .format(self.name, self.id, self.inside_dht, self.successor_id)

    def __repr__(self):
        return self.__str__()