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
    
    # Create timezone-aware datetime
    dar_tz = pytz.timezone('Africa/Dar_es_Salaam')
    if datetime_obj.tzinfo is None:
        datetime_obj = dar_tz.localize(datetime_obj)
    
    # Calculate sun position
    sun = get_sun(lat, lon, datetime_obj)
    
    # Convert to degrees
    azimuth = math.degrees(sun['azimuth'])
    elevation = math.degrees(sun['elevation'])
    
    # Normalize azimuth to 0-360
    azimuth = (azimuth + 360) % 360
    
    return azimuth, elevation

def determine_best_side(travel_dir: float, sun_azimuth: float, translations, lang):
    """Determine which side of the vehicle to sit on for shade"""
    # Calculate the relative angle of the sun to the direction of travel
    relative_angle = (sun_azimuth - travel_dir + 360) % 360
    
    # If sun is on the left side (90° to 270°), sit on the right
    # If sun is on the right side (270° to 90°), sit on the left
    if 90 <= relative_angle <= 270:
        return translations.get("sit_right", "Sit on the right side")
    else:
        return translations.get("sit_left", "Sit on the left side")
