
# https://developer.android.com/reference/android/bluetooth/le/BluetoothLeAdvertiser
# https://developer.android.com/reference/android/bluetooth/le/BluetoothLeScanner
# https://stackoverflow.com/questions/27893804/udp-client-server-socket-in-python

import socket
import threading
import time

UDP_SERVER_IP = '127.0.0.1'
UDP_SERVER_PORT = 50000

# Maximum number of bytes sent
UDP_PACKET_SIZE = 1024

class UdpClient:
    """UDP client for communicating with the simulation server"""
    def __init__(self):
        self.scanner = None

        # Create a socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Create a thread for receiving incoming messages
        self.thread = threading.Thread(target=self.thread_function, daemon=True)
        self.thread.start()

    def thread_function(self):
        # Loop forever
        while True:
            # Wait for an incoming UDP datagram
            data, addr = self.sock.recvfrom(UDP_PACKET_SIZE)
            if self.scanner:
                self.scanner.receive(data)

    def send(self, data):
        """Sends one UDP datagram to the simulation server"""
        self.sock.sendto(data, (UDP_SERVER_IP, UDP_SERVER_PORT))

client = UdpClient()

class BluetoothLeScanner:
    """Minimal simulation of the BluetoothLeScanner class in the Android SDK"""

    def __init__(self, callback):
        self.callback = callback
        client.scanner = self

    def receive(self, data):
        """This method gets called when BLE data is received"""
        if self.callback:
            self.callback(data)

class BluetoothLeAdvertiser:
    """Minimal simulation of the BluetoothLeAdvertiser class in the Android SDK"""

    def __init__(self):
        self.thread = None
        self.stopping = False
        self.interval = 1000
        self.periodic_data = b''

    def start_advertising(self, interval=1000, periodic_data=b''):
        """The device will start advertising data at a set interval"""

        print(f'Advertising {periodic_data}')

        self.stop_advertising()
        self.interval = interval
        self.periodic_data = periodic_data
        self.thread = threading.Thread(target=self.thread_function, daemon=True)
        self.stopping = False
        self.thread.start()

    def stop_advertising(self):
        """The device will stop advertising"""

        if self.thread:
            self.stopping = True
            self.thread.join()
            self.thread = None

    def thread_function(self):
        time_left = 0

        # As long as stop_advertising has not been called, loop forever
        # Count down by 100 ms at a time, so that stopping the thread doesn't block for too long
        while not self.stopping:
            time.sleep(0.1)
            time_left -= 100

            # Check if it's time to advertise
            if time_left <= 0:
                # Add another interval for the next countdown
                time_left += self.interval
                client.send(self.periodic_data)
