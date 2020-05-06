
from math import sin, cos, sqrt, atan2, radians, degrees
EARTH_RADIUS = 6378137

def distance(lat1, lng1, lat2, lng2):
    """Calculate distance in meters between two lat/lng positions"""

    # Convert from degrees to radians
    lat1 = radians(lat1)
    lng1 = radians(lng1)
    lat2 = radians(lat2)
    lng2 = radians(lng2)

    # Difference in latitude and longitude
    dlng = lng2 - lng1
    dlat = lat2 - lat1

    # https://stackoverflow.com/a/19412565/549471
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlng / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return c * EARTH_RADIUS

def move(lat, lng, meters, bearing):
    """Calculate new lat/lng position by moving a number of meters following a bearing in degrees"""

    # https://gis.stackexchange.com/a/2980/62117

    # Offsets in meters
    north = meters * cos(radians(bearing))
    east = meters * sin(radians(bearing))

    # Offsets in radians
    dlat = north / EARTH_RADIUS
    dlng = east / (EARTH_RADIUS * cos(radians(lat)))

    return lat + degrees(dlat), lng + degrees(dlng)

def bearing(lat_from, lng_from, lat_to, lng_to):
    """Calculate the bearing from one lat/lng position to another"""

    # Convert from degrees to radians
    lat1 = radians(lat_from)
    lng1 = radians(lng_from)
    lat2 = radians(lat_to)
    lng2 = radians(lng_to)

    # Longitudinal difference
    dlng = lng2 - lng1

    # https://stackoverflow.com/a/15516993/549471
    y = sin(dlng) * cos(lat2)
    x = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlng)
    bearing = degrees(atan2(y, x))
    return (bearing + 360) % 360

def geofence(lat, lng, min_lat, max_lat, min_lng, max_lng):
    """Limits a position to a geo-fence"""
    outside = False

    # Limit latitude
    if lat < min_lat:
        outside = True
        lat = min_lat
    elif lat > max_lat:
        outside = True
        lat = max_lat

    # Limit longitude
    if lng < min_lng:
        outside = True
        lng = min_lng
    elif lng > max_lng:
        outside = True
        lng = max_lng

    return lat, lng, outside

def avoid_circle(lat, lng, center_lat, center_lng, radius):
    """Avoids positioning inside a circle"""
    dist = distance(lat, lng, center_lat, center_lng)
    bear = bearing(lat, lng, center_lat, center_lng)
    if dist < radius:
        print(f'Too close to hospital! dist={dist}, bear={bear}. Moving {radius - dist} m in bearing {bear + 180}.')
        return move(lat, lng, radius - dist, bear + 180)
    else:
        return lat, lng
