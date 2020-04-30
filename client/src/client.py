
import os
import random
import time
from fake_android import BluetoothLeAdvertiser, BluetoothLeScanner

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
