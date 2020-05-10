
import os
import random
from source import timeframework as time
import time as real_time
import threading
import secrets
import sys
import hmac
import hashlib
import urllib.request
import source.timeframework
from fake_android import BluetoothLeAdvertiser, BluetoothLeScanner, UdpClient
from source import timeframework

class Client: 
    """ This class represents a device which broadcasts Ephemerals ID (EphIDs) to other devices nearby 
        It includes 3 files: one with the devices Secrete Key (Sk) for the last 14 days
        the second containing the list of all EphIDs received from other devices
        the third with the declared infected Sks. 
        The device receives EphIDs over a simulated Bluetooth connection"""
    
    def __init__(self, name, udp_client):
        #an empty set#
        self.udp_client= udp_client
        self.unique_id = set()
        self.key0 = None
        self.name = name
        self.start_broadcast()
        self.start_listen_to_ephids()
        self.start_download_infected_sk()
       
        udp_client.actor = self
 
    def start_broadcast(self):
        """starting the broadcast thread"""
        self.broadcast_thread = threading.Thread(target=self.broadcasting_ids_thread)
        self.broadcast_thread.start()
    
     #thread#
    def broadcasting_ids_thread(self):
        #send out the EphIDs, every 15 minutes pick a new one. 
        #every two minutes creates a new SK
        
        # Create an advertiser
        advertiser = BluetoothLeAdvertiser(self.name, self.udp_client)
        while True:
            self.generate_key()
            eph_ids= self.generate_ephids(self.key)
            for eph_id in eph_ids:
                advertiser.start_advertising(1000, eph_id)
                time.task_sleep(15 * 60)
    
    def generate_key(self):
        #generate a crypthographically strong random secret key using SHA256
        if self.key0 is None:
            self.key0 = secrets.token_bytes(16)
            self.key0_time = timeframework.get_today_index()
            self.key = self.key0
        else:
            self.key= self.get_next_key(self.key)
    
    def get_next_key(self, key):
        sha = hashlib.sha256()
        sha.update(key)
        return sha.digest()
    
    def generate_ephids(self, key):
        #randomize order#
        eph_ids = []
        hashed_key= hmac.new(key, digestmod='sha256')
        for i in range(0, 24 * 4):
            #use hmac to generate ids #
            hashed_key.update(bytearray([i]))
            eph_id=hashed_key.digest()
            eph_ids.append(eph_id)
        #shuffle the ids#
        random.shuffle(eph_ids)
        return eph_ids
   
    def start_listen_to_ephids(self):
        """starting the thread that listen to other devices"""
        bluetooth_scanner = BluetoothLeScanner(self.receive_ephid, self.udp_client)
  
    def receive_ephid(self, ephid):
        with open(f'Heard_EphIds{self.name}.txt', 'a') as file:
            if ephid not in self.unique_id:
                self.unique_id.add(ephid)
                file.write(ephid.hex())
                file.write('\n')
    
    def start_download_infected_sk(self):
        self.download_thread = threading.Thread(target=self.download_infected_thread)
        self.download_thread.start()
   
    def download_infected_thread(self):
        """ download the list with the sks (for the first infected day) of those pepole who have been declared infected"""
        while True:
            #read from the health care database#
            with open('healthCareDataBase.txt', 'r') as file:
                sk_infected_list= file.readlines()

                #create ephIds#
                for sk_and_time in sk_infected_list:
                    sk = sk_and_time.split(',')[0]
                    sk = bytearray.fromhex(sk)
                    timestamp =  sk_and_time.split(',')[1]
                    timestamp = int(timestamp.strip())
                    #loop from time of sk to today in simulated world
                    for t in range(timestamp, timeframework.get_today_index()):
                        infected_ephids= self.generate_ephids(sk)
                        sk = self.get_next_key(sk)
                        for infected_ephid in infected_ephids:
                            #check if there is a match#
                            if infected_ephid in self.unique_id:
                                #do it bigger and red
                                print("Warning. You have been in contact with a carrier of COVID-19.")
                                print("Please isolate yourself and check if you are a carrier")
                                #communicate with the simutation framework
                                urllib.request.urlopen(f'http://localhost:8008/warning?name={self.name}')
                                #remove infected ephids from heard ids#
                                self.unique_id = self.unique_id - set(infected_ephids)
                                return
            # Do this every 4 hours
            time.task_sleep(4 * 60 * 60)
    
    def upload_key_and_time(self,time):
        """it takes the first day of being contagious and it create its Sk for that day and 
           and uploads its Sk and timestamp"""
        sk = self.key0
        for k in range(self.key0_time, time):
            sk = self.get_next_key(sk)
        with open('healthCareDataBase.txt', 'a') as output:
            output.write(f'{sk.hex()} , {time}\n')

argument = sys.argv[1]
if argument.isnumeric():
    #A number was passed in. Start this many clients#
    number_of_clients = int(argument)
    for i in range(0, number_of_clients):
        client = Client(f'Client{i}',  UdpClient())
else:
    #A string was passed in. Start one client with this name#
    client = Client(argument, UdpClient())
