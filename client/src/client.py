
import os
import random
import time
import threading
import secrets
import sys
import hmac
from fake_android import BluetoothLeAdvertiser, BluetoothLeScanner

class Client: 
    """ This class represents a device which broadcasts Ephemerals ID (EphIDs) to other devices nearby 
        It includes 3 files: one with the devices Secrete Key (Sk) for the last 14 days
        the second containing the list of all EphIDs received from other devices
        the third with the declared infected Sks. 
        The device receives EphIDs over a simulated Bluetooth connection"""
    
    def __init__(self, id):
        #an empty set#
        self.unique_id = set()
        self.id = id
        self.start_broadcast()
        self.start_listen_to_ephids()
        self.start_download_infected_sk()
    
 
    def start_broadcast(self):
        """starting the broadcast thread"""
        self.broadcast_thread = threading.Thread(target=self.broadcasting_ids_thread)
        self.broadcast_thread.start()
    
     #thread#
    def broadcasting_ids_thread(self):
        #send out the EphIDs, every 5 sec send a new. 
        #every two minutes creates a new SK
        
        # Create an advertiser
        advertiser = BluetoothLeAdvertiser()
        while True:
            self.generate_key()
            self.add_key_to_file()
            eph_ids= self.generate_ephids(self.key)
            for eph_id in eph_ids:
                advertiser.start_advertising(1000, eph_id)
                time.sleep(random.uniform(4, 6))
        
    def generate_key(self):
        #generate a crypthographically strong random secret key
        self.key = secrets.token_bytes(32)
    
    def add_key_to_file(self):
        with open(f'Sk{self.id}.txt', 'a') as file:
            file.write(self.key.hex())
            file.write('\n')
    
    def generate_ephids(self,key):
        #randomize order#
        eph_ids = []
        hashed_key= hmac.new(key, digestmod='sha256')
        for i in range(0, 24):
            #use hmac to generate ids #
            hashed_key.update(bytearray([i]))
            eph_id=hashed_key.digest()[:16]
            eph_ids.append(eph_id)
        #shuffle the ids#s
        random.shuffle(eph_ids)
        return eph_ids
   
    def start_listen_to_ephids(self):
        """starting the thread that listen to other devices"""
        bluetooth_scanner = BluetoothLeScanner(self.receive_ephid)
  
    def receive_ephid(self, ephid):
        with open(f'Heard_EphIds{self.id}.txt', 'a') as file:
            if ephid not in self.unique_id:
                self.unique_id.add(ephid)
                file.write(ephid.hex())
                file.write('\n')
    
    def start_download_infected_sk(self):
        """ download the list with the sk of those pepole who have been declared infected"""
        self.download_thread = threading.Thread(target=self.download_infected_thread)
        self.download_thread.start()
   
    def download_infected_thread(self):
        while True:
            #read from the health care database#
            with open('healthCareDataBase.txt', 'r') as file:
                sk_infected_list= file.readlines()
                #create ephIds#
                for sk in sk_infected_list:
                    infected_ephids= self.generate_ephids(bytearray.fromhex(sk.strip()))
                    for infected_ephid in infected_ephids:
                        #check if there is a match#
                        if infected_ephid in self.unique_id:
                            print("Warning. You have been in contact with a carrier of COVID-19.")
                            print("Please isolate yourself and check if you are a carrier")
                            return
            time.sleep(120)

client = Client(sys.argv[1])
