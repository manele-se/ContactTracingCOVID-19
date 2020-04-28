
import random
import socket
import threading
import time
from device import Device

UDP_PACKET_SIZE = 1024
MIN_DISTANCE = 40
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

    def start(self):
        # Start the UDP server thread
        self.bluetooth_thread = threading.Thread(name='bluetooth', target=self.bluetooth_run, daemon=True)
        self.bluetooth_thread.start()

    def bluetooth_run(self):
        """The thread running the UDP server"""

        # Start a UDP socket and listen for incoming packets
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.udp_ip, self.udp_port))

        while True:
            # Wait for one packet to arrive
            data, addr = sock.recvfrom(UDP_PACKET_SIZE)
            self.handle_incoming_broadcast(sock, data, addr)

    def handle_incoming_broadcast(self, sock, data, sender_addr):
        # Check if the sender's address is already known or not
        if sender_addr in self.devices_by_addr:
            sender = self.devices_by_addr[sender_addr]
        else:
            # This address is unknown; create a new device and store it
            sender = Device()
            self.devices_by_addr[sender_addr] = sender

        # Loop over all other devices
        for receiver_addr, receiver in self.devices_by_addr.items():
            if sender == receiver:
                continue

            # Get the distance between sender and receiver
            distance = sender.distance_to(receiver)

            # "Fake" a signal strength <= 1.0
            signal_strength = 1.0 / (1.0 + distance)

            # Signal strength of 40 meters away have a   0 % chance of arriving
            # Signal strength of  3 meters away have a 100 % chance of arriving
            threshold = random.uniform(MIN_STRENGTH, MAX_STRENGTH)
            if signal_strength > threshold:
                # If signal is strong enough, relay the packet to the receiver
                sock.sendto(data, receiver_addr)

    def tick(self, seconds_passed):
        for device in self.devices_by_addr.values():
            device.tick(seconds_passed)

server = Server()
server.start()

while True:
    time.sleep(1.0)
    server.tick(1.0)
