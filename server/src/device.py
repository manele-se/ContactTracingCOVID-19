
import random
import threading
import time

from latlng import distance, move, bearing, geofence, avoid_circle

# This geo-fence is a rough square in Lindholmen, Göteborg
MIN_LAT = 57.7064
MAX_LAT = 57.7074

MIN_LNG = 11.9359
MAX_LNG = 11.9393

HOSPITAL_LAT = 57.706976
HOSPITAL_LNG = 11.937991
HOSPITAL_RADIUS = 25

# Speeds are in m/s
MIN_SPEED = 1
MAX_SPEED = 2

# Rotation speeds are in degrees/s
MIN_ROTATION_SPEED = -5
MAX_ROTATION_SPEED = 5

class Device:
    """Representation of a virtual Bluetooth-simulating device,
       with a lat/lng position in a virtual world, that moves
       around randomly, and that can be told to move to a place."""
    next_id = 1

    def __init__(self, addr, name):
        """Constructor for the Device class"""

        # Give the device a random position and a random movement pattern
        (self.lat, self.lng) = Device.randomize_position()
        (self.bearing, self.speed, self.rotation_speed) = Device.randomize_movement()

        # Give the device an internal name and store the UDP address
        self.name = name
        self.addr = addr

        # Keep track of last action
        self.last_action = time.time()
        self.zombie = False

        # Start a thread that makes the device move around
        self.thread = threading.Thread(name=self.name, target=self.thread_function, daemon=True)
        self.thread.start()
        self.tick_callback = None

        # Start without movement
        self.still = True

        # Increment the ID for the next device
        Device.next_id += 1

    def thread_function(self):
        """Thread for moving the device around"""

        # Loop forever
        while not self.zombie:
            # Sleep a random amount of time and move some distance
            time_to_sleep = random.uniform(0.2, 0.4)
            time.sleep(time_to_sleep)
            if not self.still:
                self.tick(time_to_sleep)

    def distance_to(self, other_device):
        """Returns the distance in meters to another device"""

        return distance(self.lat, self.lng, other_device.lat, other_device.lng)

    def bearing_to(self, other_device):
        """Returns the bearing in degrees to another device"""

        return bearing(self.lat, self.lng, other_device.lat, other_device.lng)

    def tick(self, seconds_passed):
        """Performs movement of the device"""

        # Update the position
        (self.lat, self.lng) = move(self.lat, self.lng, self.speed * seconds_passed, self.bearing)
        # Make sure position is inside the geo-fence
        (self.lat, self.lng, was_outside) = geofence(self.lat, self.lng, MIN_LAT, MAX_LAT, MIN_LNG, MAX_LNG)
        # If the position was outside, pick a new random movement
        if was_outside:
            (self.bearing, self.speed, self.rotation_speed) = Device.randomize_movement()
        (self.lat, self.lng) = avoid_circle(self.lat, self.lng, HOSPITAL_LAT, HOSPITAL_LNG, HOSPITAL_RADIUS)

        # Update the bearing using the rotational speed
        self.bearing = (self.bearing + self.rotation_speed * seconds_passed) % 360

        # Notify listener
        if self.tick_callback:
            self.tick_callback(self.name, self.lat, self.lng, self.bearing)

    @staticmethod
    def randomize_position():
        """Returns a random location inside the geo-fence"""

        lat = random.uniform(MIN_LAT, MAX_LAT)
        lng = random.uniform(MIN_LNG, MAX_LNG)

        lat, lng = avoid_circle(lat, lng, HOSPITAL_LAT, HOSPITAL_LNG, HOSPITAL_RADIUS)

        return lat, lng

    @staticmethod
    def randomize_movement():
        """Returns a random direction, speed and rotation speed"""

        bearing = random.uniform(0, 360)
        speed = random.uniform(MIN_SPEED, MAX_SPEED)
        rotation_speed = random.uniform(MIN_ROTATION_SPEED, MAX_ROTATION_SPEED)

        return bearing, speed, rotation_speed
