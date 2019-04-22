# coding: utf-8

import time
import pickle
import socket
import random
import logging
import argparse

from Restaurant import Restaurant
from Waiter import Waiter
from Chef import Chef
from Clerk import Clerk

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S')


def main():

    restaurant = Restaurant()
    waiter = Waiter()
    chef = Chef()
    clerk = Clerk()

    # O start vai a cada entidade e vai inciar uma thread
    restaurant.start()
    waiter.start()
    chef.start()
    clerk.start()

    restaurant.join()
    waiter.join()
    chef.join()
    clerk.join()

    return 0


if __name__ == '__main__':
    main()
