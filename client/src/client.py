
import os
import random
import time
from fake_android import BluetoothLeAdvertiser, BluetoothLeScanner

class Client: 
    """ This class represents a device which broadcasts Ephemerals ID (EphIDs) to other devices nearby 
        It includes 3 files: one with the devices Secrete Key (Sk) for the last 14 days
        the second containing the list of all EphIDs received from other devices
        the third with the declared infected Sks. 
        The device receives EphIDs over a simulated Bluetooth connection"""
    
    def __init__(self):
        self.generate_key()
        self.add_key_to_file()
        self.generate_ephids()
        self.broadcast()
        self.get_ephids()
        
    def generate_key(self):
        self.key = '123'
    
    def add_key_to_file(self):
        with open('Sk.txt', 'a') as file:
            file.write(self.key)
            file.write('\n')
    
    def generate_ephids(self):
        pass
    
    def broadcast(self):
        pass
    
    def get_ephids(self):
        pass


client = Client()






"""
def receive(data):
    print(f'Received: {data}')

# Create an advertiser
advertiser = BluetoothLeAdvertiser()

# Start advertising
data = os.urandom(4)  # get 4 random bytes
advertiser.start_advertising(1000, data)

# Create a scanner
scanner = BluetoothLeScanner(receive)

# Loop forever
while True:
    time.sleep(1)
"""