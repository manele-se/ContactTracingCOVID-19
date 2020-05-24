
# https://www.tornadoweb.org/en/stable/websocket.html

import json
import random
import socket
import sys
import threading
import time as real_time
import tornado.ioloop
import tornado.web
import tornado.websocket
import asyncio
from sys import platform
from doctor import Doctor
from device import Device, State

# Maximum number of bytes sent
UDP_PACKET_SIZE = 65507

# Signal strength of 10 meters away have a   0 % chance of arriving
# Signal strength of  5 meters away have a 100 % chance of arriving
MIN_DISTANCE = 5
MAX_DISTANCE = 10

# Port number for the web server
WWW_PORT = 8008

# Maximum number of seconds without a Bluetooth broadcast
ZOMBIE_MAX_AGE = 5


class Server:
    """Acts as intermediary for UDP packets, simulating Bluetooth LE between devices that are close
       enough to each other."""

    def __init__(self, wwwroot_path='wwwroot', udp_ip='127.0.0.1', udp_port=50000):
        """Creates and starts the simulation server"""
        self.wwwroot_path = wwwroot_path
        self.udp_ip = udp_ip
        self.udp_port = udp_port

        # This dict stores devices by their internal name
        self.devices_by_name = dict()

        # Start a thread to clean up zombie devices
        self.zombie_thread = threading.Thread(
            name='zombies', target=self.zombie_thread_function, daemon=True)
        self.zombie_thread.start()

        # Start the UDP server thread for simulating bluetooth
        self.bluetooth_thread = threading.Thread(
            name='bluetooth', target=self.bluetooth_thread_function, daemon=True)
        self.bluetooth_thread.start()

        # create a doctor
        self.doctor = Doctor(self)

        # Start the web server, hosting the Google Maps frontend
        WebSocketHandler.server = self
        MoveRequestHandler.server = self
        WarningRequestHandler.server = self
        self.web_socket_handlers = set()
        tornado_app = tornado.web.Application([
            (r'/ws', WebSocketHandler),
            (r'/move', MoveRequestHandler),
            (r'/warning', WarningRequestHandler),
            (r'/(.*)', tornado.web.StaticFileHandler,
             {'path': self.wwwroot_path, 'default_filename': 'index.html'})

        ])

        tornado_app.listen(WWW_PORT)
        self.ioloop = tornado.ioloop.IOLoop.instance()
        self.ioloop.start()

    def zombie_thread_function(self):
        """The thread cleaning up zombie devices"""

        # Loop forever
        while True:
            real_time.sleep(0.5)
            now = real_time.time()
            threshold = now - ZOMBIE_MAX_AGE
            # Get all zombies
            zombies = list(filter(lambda d: d.last_action < threshold and not d.name.startswith(
                'Mallory'), self.devices_by_name.values()))
            for zombie in zombies:
                print(f'Deleting zombie {zombie.name}')
                del self.devices_by_name[zombie.name]
                zombie.zombie = True
                zombie.tick_callback = None
                # Send removal to WebSocket clients
                for ws_handler in self.web_socket_handlers:
                    ws_handler.send_device_removed(zombie.name)

    def bluetooth_thread_function(self):
        """The thread running the UDP server"""

        # Start a UDP socket and listen for incoming packets
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.udp_ip, self.udp_port))

        # Loop forever
        while True:
            # Wait for one UDP datagram to arrive
            try:
                data, addr = self.sock.recvfrom(UDP_PACKET_SIZE)
                self.handle_incoming_broadcast(self.sock, data, addr)
            except:
                pass

    def handle_incoming_broadcast(self, sock, datagram, sender_addr):
        """When an incoming BLE broadcast arrives, relay it to all other devices that are close enough"""

        message_json = datagram.decode('utf-8')

        try:
            message_object = json.loads(message_json)
        except json.decoder.JSONDecodeError:
            print('Error decoding json!')
            print(message_json)
            return

        if type(message_object) is list:
            self.show_location_trails(message_object)
        else:
            sender_name = message_object['name']
            data = bytearray.fromhex(message_object['data'])

            # Get the Device instance for this address, or create a new one if this is a new address
            sender = self.get_or_create_device(sender_addr, sender_name)
            sender.last_action = real_time.time()
            if sender.state == State.INFECTED:
                return

            # Send broadcast to WebSocket clients
            for ws_handler in self.web_socket_handlers:
                ws_handler.send_device_broadcast(
                    sender.name, sender.lat, sender.lng)

            # Use a random threshold to sort of simulate real-world conditions
            threshold = random.uniform(MIN_DISTANCE, MAX_DISTANCE)

            # Loop over all other devices
            for receiver in self.devices_by_name.values():
                if sender == receiver:
                    continue

                # Get the distance between sender and receiver
                distance = sender.distance_to(receiver)

                if distance < threshold:
                    # If signal is strong enough, relay the packet to the receiver
                    print(f'Relaying from {sender.name} to {receiver.name}')
                    self.send_info_to_client(receiver.name, {
                        'data_type': 'bluetooth',
                        'information': data.hex()
                    })
                    # Send receive event to WebSocket clients
                    for ws_handler in self.web_socket_handlers:
                        ws_handler.send_device_received(
                            receiver.name, receiver.lat, receiver.lng)

    def show_location_trails(self, location):
        # sort list by timestamp
        location_sorted = sorted(location, key=lambda item: item[2])
        # Send receive event to WebSocket clients

        for ws_handler in self.web_socket_handlers:
            ws_handler.send_location_trail(location_sorted)

    def send_info_to_client(self, name, info):
        info_str = json.dumps(info)
        # convert i byte with encoding
        info_bytes = info_str.encode('utf-8')
        # pick the address of a device
        addr = self.devices_by_name[name].addr
        self.sock.sendto(info_bytes, addr)

    def get_or_create_device(self, sender_addr, sender_name):
        """If the sender's address is known, return the device for that address, otherwise add a new device"""

        # Check if the sender's address is already known or not
        if sender_name in self.devices_by_name:
            # This address is known; return the already known device
            return self.devices_by_name[sender_name]
        else:
            # This address is unknown; create a new device and store it
            sender = Device(sender_addr, sender_name)
            self.devices_by_name[sender_name] = sender
            print(f'Discovered new device "{sender_name}"')

            # Start listening to the device's movements
            sender.tick_callback = self.device_tick_callback
            return sender

    def move_device(self, name, lat, lng):
        """The device was moved by "the hand of God" (in the web interface)"""
        if name in self.devices_by_name:
            device = self.devices_by_name[name]
            device.lat = lat
            device.lng = lng
            self.device_tick_callback(name, lat, lng, device.bearing)
            device.still = True
            if device.is_in_hospital():
                device.state = State.INFECTED
                self.doctor.communicate_test_result(name)
                # Send changes to WebSocket clients
                for ws_handler in self.web_socket_handlers:
                    ws_handler.send_device_in_hospital(name)
            elif device.state == State.INFECTED:
                device.state = State.HEALTHY
                # Send changes to WebSocket clients
                for ws_handler in self.web_socket_handlers:
                    ws_handler.send_device_healthy(name)

    def stop_moving_device(self, name):
        """The device was grabbed. The person decided to stop moving."""
        if name in self.devices_by_name:
            device = self.devices_by_name[name]
            device.still = True

    def toggle_moving_device(self, name):
        """The device was clicked. The person decided to change their mind about moving."""
        if name in self.devices_by_name:
            device = self.devices_by_name[name]
            device.still = not device.still

    def device_tick_callback(self, name, lat, lng, bearing):
        """This callback is called when a device moves"""

        # Send movement to WebSocket clients
        for ws_handler in self.web_socket_handlers:
            ws_handler.send_device_moved(name, lat, lng, bearing)

         # send position to fake-gps
        self.send_info_to_client(name, {
            'data_type': 'location',
            'lat': lat,
            'lng': lng
        })

    def send_action_to_client(self, action, data):
        """send a message to client"""

    def tick(self, seconds_passed):
        pass


class MoveRequestHandler(tornado.web.RequestHandler):
    """Http handler for move commands performed in the web user interface"""

    server = None

    def get(self):
        device_name = self.get_argument('name')
        action = self.get_argument('action')
        device = MoveRequestHandler.server.devices_by_name[device_name]

        if action == 'stop':
            device.still = True
        elif action == 'toggle':
            device.still = not device.still


class WarningRequestHandler(tornado.web.RequestHandler):
    """Http handler for warning commands sent from the client"""
    server = None

    def get(self):
        device_name = self.get_argument('name')
        # if infected do not send to the client to change
        device = WarningRequestHandler.server.devices_by_name[device_name]
        if device.state == State.INFECTED:
            return

        # Send changes to WebSocket clients
        for ws_handler in WarningRequestHandler.server.web_socket_handlers:
            ws_handler.send_warning_to_device(device_name)


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

        message = json.loads(message)
        name = message['name']
        action = message['action']
        if action == 'move':
            lat = message['lat']
            lng = message['lng']
            WebSocketHandler.server.move_device(name, lat, lng)
        elif action == 'stop':
            WebSocketHandler.server.stop_moving_device(name)
        elif action == 'toggle':
            WebSocketHandler.server.toggle_moving_device(name)

    def send_device_moved(self, name, lat, lng, bearing):
        """Send information to the client about a device movement"""
        json_data = json.dumps({
            'action': 'move',
            'name': name,
            'lat': lat,
            'lng': lng,
            'bearing': bearing
        })
        self.send_json(json_data)

    def send_device_removed(self, name):
        """Send information to the client about a device removal"""
        json_data = json.dumps({
            'action': 'remove',
            'name': name
        })
        self.send_json(json_data)

    def send_device_in_hospital(self, name):
        """Send information to the browser about a device changing color"""
        json_data = json.dumps({
            'action': 'change_color_red',
            'name': name
        })
        self.send_json(json_data)

    def send_warning_to_device(self, name):
        """Send information to the client about a device changing color"""
        json_data = json.dumps({
            'action': 'change_color_yellow',
            'name': name
        })
        self.send_json(json_data)

    def send_device_healthy(self, name):
        """Send information to the client about a device changing color"""
        json_data = json.dumps({
            'action': 'change_color_green',
            'name': name
        })
        self.send_json(json_data)

    def send_device_malicious(self, name):
        """Send information to the client about a device changing color"""
        json_data = json.dumps({
            'action': 'change_color_purple',
            'name': name
        })
        self.send_json(json_data)

    def send_device_broadcast(self, name, lat, lng):
        """Send information to the client about a device broadcast"""
        json_data = json.dumps({
            'action': 'broadcast',
            'name': name,
            'lat': lat,
            'lng': lng
        })
        self.send_json(json_data)

    def send_device_received(self, name, lat, lng):
        """Send information to the client about a device broadcast"""
        json_data = json.dumps({
            'action': 'receive',
            'name': name,
            'lat': lat,
            'lng': lng
        })
        self.send_json(json_data)

    def send_location_trail(self, trail):
        """Send information to the client about a location trail"""
        json_data = json.dumps({
            'action': 'location_trail',
            'trail': trail
        })

        self.send_json(json_data)

    def send_json(self, json_data):
        # For thread safety, this message must be sent on the event loop thread
        # https://www.tornadoweb.org/en/stable/ioloop.html#tornado.ioloop.IOLoop.add_callback
        WebSocketHandler.server.ioloop.add_callback(
            self.write_message, json_data)


if platform == 'win32':
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy())  # python-3.8.0a4

wwwroot_path = sys.argv[1]
server = Server(wwwroot_path=wwwroot_path)

while True:
    real_time.sleep(1.0)
    server.tick(1.0)
