
import random
import time
from fake_android import BluetoothLeAdvertiser, BluetoothLeScanner

def receive(data):
    print(f'Received: {data}')

# Create an advertiser
advertiser = BluetoothLeAdvertiser()

# Start advertising
advertiser.start_advertising(1000, str(random.randrange(1000, 9999)).encode('utf-8'))

# Create a scanner
scanner = BluetoothLeScanner(receive)

# Loop forever
while True:
    time.sleep(1)
