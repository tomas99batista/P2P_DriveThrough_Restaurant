# coding: utf-8

import socket
import threading
import logging
import pickle
import time

def contains_successor(identification, successor, node):
            if identification < node <= successor:
                return True
            elif successor < identification and (node > identification or node < successor):
                return True
            return False

def work(seconds):
    time.sleep(seconds)