
import random

from latlng import distance, move, bearing, geofence

# This geo-fence is a rough square in LindHolmen, Göteborg
MIN_LAT = 57.7047
MAX_LAT = 57.7093

MIN_LNG = 11.9281
MAX_LNG = 11.9379

# Speeds are in m/s
MIN_SPEED = 5
MAX_SPEED = 10

# Rotation speeds are in degrees/s
MIN_ROTATION_SPEED = -5
MAX_ROTATION_SPEED = 5

class Device:
    """Representation of a virtual Bluetooth-simulating device,
       with a lat/lng position in a virtual world, that moves
       around randomly, and that can be told to move to a place."""

    def __init__(self):
        """Constructor for the Device class"""
        (self.lat, self.lng) = Device.randomize_position()
        (self.bearing, self.speed, self.rotation_speed) = Device.randomize_movement()

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

        # Update the bearing using the rotational speed
        self.bearing = (self.bearing + self.rotation_speed * seconds_passed) % 360

    @staticmethod
    def randomize_position():
        """Returns a random location inside the geo-fence"""
        lat = random.uniform(MIN_LAT, MAX_LAT)
        lng = random.uniform(MIN_LNG, MAX_LNG)

        return lat, lng

    @staticmethod
    def randomize_movement():
        """Returns a random direction, speed and rotation speed"""
        bearing = random.uniform(0, 360)
        speed = random.uniform(MIN_SPEED, MAX_SPEED)
        rotation_speed = random.uniform(MIN_ROTATION_SPEED, MAX_ROTATION_SPEED)

        return bearing, speed, rotation_speed
