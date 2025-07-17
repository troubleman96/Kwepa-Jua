from math import atan2, radians, degrees, sin, cos
from datetime import datetime
from pysolar.solar import get_azimuth

def calculate_bearing(start_lat, start_lon, end_lat, end_lon):
    start_lat, start_lon = radians(start_lat), radians(start_lon)
    end_lat, end_lon = radians(end_lat), radians(end_lon)
    dlon = end_lon - start_lon
    x = sin(dlon) * cos(end_lat)
    y = cos(start_lat) * sin(end_lat) - sin(start_lat) * cos(end_lat) * cos(dlon)
    return (degrees(atan2(x, y)) + 360) % 360

def get_sun_azimuth(dt: datetime, lat: float, lon: float):
    return get_azimuth(lat, lon, dt)

def determine_best_side(travel_dir: float, sun_azimuth: float):
    relative_angle = (sun_azimuth - travel_dir + 360) % 360
    return "Sit left (shade side)" if 90 < relative_angle < 270 else "Sit right (shade side)"
