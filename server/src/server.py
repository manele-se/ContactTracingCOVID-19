
# https://www.tornadoweb.org/en/stable/websocket.html

import json
import random
import socket
import threading
import time
import tornado.ioloop
import tornado.web
import tornado.websocket
from device import Device

# Maximum number of bytes sent
UDP_PACKET_SIZE = 1024

# Signal strength of 10 meters away have a   0 % chance of arriving
# Signal strength of  5 meters away have a 100 % chance of arriving
MIN_DISTANCE = 5
MAX_DISTANCE = 10

# Port number for the web server
WWW_PORT = 8008

class Server:
    """Acts as intermediary for UDP packets, simulating Bluetooth LE between devices that are close
       enough to each other."""

    def __init__(self, udp_ip='127.0.0.1', udp_port=50000):
        """Creates and starts the simulation server"""
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
        WebSocketHandler.server = self
        self.web_socket_handlers = set()
        tornado_app = tornado.web.Application([
            (r'/ws', WebSocketHandler),
            (r'/(.*)', tornado.web.StaticFileHandler, {'path': './wwwroot', 'default_filename': 'index.html'})
        ])
        tornado_app.listen(WWW_PORT)
        self.ioloop = tornado.ioloop.IOLoop.instance()
        self.ioloop.start()

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

        # Get the Device instance for this address, or create a new one if this is a new address
        sender = self.get_of_create_device_from_addr(sender_addr)

        print(f'"{sender.name}" says "{data}')

        # Send broadcast to WebSocket clients
        for ws_handler in self.web_socket_handlers:
            ws_handler.send_device_broadcast(sender.name, sender.lat, sender.lng)

        # Use a random threshold to sort of simulate real-world conditions
        threshold = random.uniform(MIN_DISTANCE, MAX_DISTANCE)

        # Loop over all other devices
        for receiver in self.devices_by_addr.values():
            if sender == receiver:
                continue

            # Get the distance between sender and receiver
            distance = sender.distance_to(receiver)

            if distance < threshold:
                # If signal is strong enough, relay the packet to the receiver
                print(f'Relaying to {receiver.name}')
                sock.sendto(data, receiver.addr)

                # Send receive event to WebSocket clients
                for ws_handler in self.web_socket_handlers:
                    ws_handler.send_device_received(receiver.name, receiver.lat, receiver.lng)

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
        """This callback is called when a device moves"""

        # Send movement to WebSocket clients
        for ws_handler in self.web_socket_handlers:
            ws_handler.send_device_moved(name, lat, lng, bearing)

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    """WebSocket connection handler for real-time updates in the web user interface"""

    server = None

    def open(self):
        """A new WebSocket connection was established"""

        # Add this handler to the server's set of handlers
        WebSocketHandler.server.web_socket_handlers.add(self)
        print('WebSocket connection opened')
        self.set_nodelay(True)

    def on_close(self):
        """This WebSocket connection was closed"""

        # Remove this handler from the server's set of handlers
        WebSocketHandler.server.web_socket_handlers.remove(self)
        print('WebSocket connection closed')

    def on_message(self, message):
        """The client sent a message to this WebSocket connection"""

        print(f'WebSocket incoming message: {message}')

    def send_device_moved(self, name, lat, lng, bearing):
        """Send information to the client about a device movement"""
        json_data = json.dumps({
            'action': 'move',
            'name': name,
            'lat': lat,
            'lng': lng,
            'bearing': bearing
        })

        # For thread safety, this message must be sent on the event loop thread
        # https://www.tornadoweb.org/en/stable/ioloop.html#tornado.ioloop.IOLoop.add_callback
        WebSocketHandler.server.ioloop.add_callback(self.write_message, json_data)

    def send_device_broadcast(self, name, lat, lng):
        """Send information to the client about a device broadcast"""
        json_data = json.dumps({
            'action': 'broadcast',
            'name': name,
            'lat': lat,
            'lng': lng
        })

        # For thread safety, this message must be sent on the event loop thread
        # https://www.tornadoweb.org/en/stable/ioloop.html#tornado.ioloop.IOLoop.add_callback
        WebSocketHandler.server.ioloop.add_callback(self.write_message, json_data)

    def send_device_received(self, name, lat, lng):
        """Send information to the client about a device broadcast"""
        json_data = json.dumps({
            'action': 'receive',
            'name': name,
            'lat': lat,
            'lng': lng
        })

        # For thread safety, this message must be sent on the event loop thread
        # https://www.tornadoweb.org/en/stable/ioloop.html#tornado.ioloop.IOLoop.add_callback
        WebSocketHandler.server.ioloop.add_callback(self.write_message, json_data)

server = Server()

while True:
    time.sleep(1.0)
    server.tick(1.0)
