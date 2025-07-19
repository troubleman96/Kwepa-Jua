import math
from datetime import datetime
import pytz

def calculate_bearing(route_data):
    """Calculate bearing between two points from route data"""
    start = route_data["start"]
    end = route_data["end"]
    
    start_lat, start_lon = math.radians(start["lat"]), math.radians(start["lon"])
    end_lat, end_lon = math.radians(end["lat"]), math.radians(end["lon"])
    dlon = end_lon - start_lon
    
    x = math.sin(dlon) * math.cos(end_lat)
    y = math.cos(start_lat) * math.sin(end_lat) - math.sin(start_lat) * math.cos(end_lat) * math.cos(dlon)
    
    bearing = math.atan2(x, y)
    bearing = math.degrees(bearing)
    bearing = (bearing + 360) % 360
    
    return bearing

def get_sun_position(datetime_obj):
    """Calculate sun position for Dar es Salaam coordinates"""
    # Dar es Salaam coordinates
    lat = -6.7924
    lon = 39.2083
    
    # Simple sun position calculation
    # This is a simplified version - for production use astral library
    hour = datetime_obj.hour + datetime_obj.minute / 60.0
    
    # Very basic sun elevation (negative at night)
    if hour < 6 or hour > 18:
        elevation = -30  # Night time
        azimuth = 180
    else:
        # Simplified day calculation
        elevation = 60 * math.sin(math.pi * (hour - 6) / 12)
        azimuth = 90 + 180 * (hour - 6) / 12
    
    return azimuth, elevation

def determine_best_side(bearing, sun_azimuth, translations, lang):
    """Determine which side of the vehicle provides better shade"""
    # Calculate relative angle between route and sun
    relative_angle = (sun_azimuth - bearing) % 360
    
    # Determine which side is better
    if 90 <= relative_angle <= 270:
        # Sun is on the left side of travel direction, sit on the right
        side_key = "sit_right" if lang == "en" else "sit_right_sw"
    else:
        # Sun is on the right side of travel direction, sit on the left  
        side_key = "sit_left" if lang == "en" else "sit_left_sw"
    
    return translations.get(side_key, "Sit on the shaded side")
