
import random
import socket
import threading
import time
from device import Device

# Maximum number of bytes sent
UDP_PACKET_SIZE = 1024

# Signal strength of 60 meters away have a   0 % chance of arriving
# Signal strength of  3 meters away have a 100 % chance of arriving
MIN_DISTANCE = 60
MAX_DISTANCE = 3
MIN_STRENGTH = 1.0 / (MIN_DISTANCE + 1)
MAX_STRENGTH = 1.0 / (MAX_DISTANCE + 1)

class Server:
    """Acts as intermediary for UDP packets, simulating Bluetooth LE between devices that are close
       enough to each other."""

    def __init__(self, udp_ip='127.0.0.1', udp_port=50000):
        """Creates and starts a UDP server"""
        self.udp_ip = udp_ip
        self.udp_port = udp_port

        # This dict stores devices by their UDP address
        self.devices_by_addr = dict()

        # This dict stores devices by their internal name
        self.devices_by_name = dict()

        # Start the UDP server thread for simulating bluetooth
        self.bluetooth_thread = threading.Thread(name='bluetooth', target=self.bluetooth_thread_function, daemon=True)
        self.bluetooth_thread.start()

        # Start the web server, hosting the Google Maps frontend
    def bluetooth_thread_function(self):
        """The thread running the UDP server"""

        # Start a UDP socket and listen for incoming packets
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.udp_ip, self.udp_port))

        # Loop forever
        while True:
            # Wait for one UDP datagram to arrive
            data, addr = sock.recvfrom(UDP_PACKET_SIZE)
            self.handle_incoming_broadcast(sock, data, addr)

    def handle_incoming_broadcast(self, sock, data, sender_addr):
        """When an incoming BLE broadcast arrives, relay it to all other devices that are close enough"""

        print(f'"{sender_addr}" says "{data}')

        # Get the Device instance for this address, or create a new one if this is a new address
        sender = self.get_of_create_device_from_addr(sender_addr)

        # Loop over all other devices
        for receiver in self.devices_by_addr.values():
            if sender == receiver:
                continue

            # Get the distance between sender and receiver
            distance = sender.distance_to(receiver)

            # "Fake" a signal strength <= 1.0
            signal_strength = 1.0 / (1.0 + distance)

            # Use a random threshold to sort of simulate real-world conditions
            threshold = random.uniform(MIN_STRENGTH, MAX_STRENGTH)
            if signal_strength > threshold:
                # If signal is strong enough, relay the packet to the receiver
                sock.sendto(data, receiver.addr)

    def get_of_create_device_from_addr(self, sender_addr):
        """If the sender's address is known, return the device for that address, otherwise add a new device"""

        # Check if the sender's address is already known or not
        if sender_addr in self.devices_by_addr:
            # This address is known; return the already known device
            return self.devices_by_addr[sender_addr]
        else:
            # This address is unknown; create a new device and store it
            sender = Device(sender_addr)
            self.devices_by_addr[sender_addr] = sender
            self.devices_by_name[sender.name] = sender
            # Start listening to the device's movements
            sender.tick_callback = self.device_tick_callback
            return sender

    def tick(self, seconds_passed):
        pass

    def device_tick_callback(self, name, lat, lng, bearing):
        print(f'{name} has moved to {lat:.6f}, {lng:.6f}')

server = Server()

while True:
    time.sleep(1.0)
    server.tick(1.0)
