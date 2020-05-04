
import os
import random
import time
import threading
import secrets
import hmac
from fake_android import BluetoothLeAdvertiser, BluetoothLeScanner

class Client: 
    """ This class represents a device which broadcasts Ephemerals ID (EphIDs) to other devices nearby 
        It includes 3 files: one with the devices Secrete Key (Sk) for the last 14 days
        the second containing the list of all EphIDs received from other devices
        the third with the declared infected Sks. 
        The device receives EphIDs over a simulated Bluetooth connection"""
    
    def __init__(self):
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
            eph_ids= self.generate_ephids()
            for eph_id in eph_ids:
                 advertiser.start_advertising(1000, eph_id)
                 time.sleep(5)
        
    def generate_key(self):
        #generate a crypthographically strong random secret key
        self.key = secrets.token_bytes(32)
    
    def add_key_to_file(self):
        with open('Sk.txt', 'a') as file:
            file.write(self.key.hex())
            file.write('\n')
    
    def generate_ephids(self):
        #randomize order#
        eph_ids=[]
        hashed_key= hmac.new(self.key,digestmod='sha256')
        for i in range (0,24):
            #use hmac to generate ids #
            hashed_key.update(bytearray([i]))
            eph_id=hashed_key.digest()
            eph_ids.append(eph_id)
        #shuffle the ids#
        random.shuffle(eph_ids)
        return eph_ids
            
            
            
           
    
   
    def start_listen_to_ephids(self):
        """starting the thread that listen to other devices"""
        pass
    
    def listen_ephids_thread(self):
        pass
    
    def start_download_infected_sk(self):
        """ download the list with the sk of those pepole who have been declared infected"""
        pass
   
    def dowload_infected_thread(self):
       pass
            


client = Client()






"""
def receive(data):
    print(f'Received: {data}')




# Create a scanner
scanner = BluetoothLeScanner(receive)

# Loop forever
while True:
    time.sleep(1)
"""