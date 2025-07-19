import math
from datetime import datetime
import pytz
from astral import LocationInfo
from astral.sun import sun

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
    """Calculate sun position for Dar es Salaam coordinates using astral library"""
    # Create location for Dar es Salaam
    city = LocationInfo("Dar es Salaam", "Tanzania", "Africa/Dar_es_Salaam", -6.7924, 39.2083)
    
    # Ensure datetime is timezone-aware
    dar_tz = pytz.timezone('Africa/Dar_es_Salaam')
    if datetime_obj.tzinfo is None:
        datetime_obj = dar_tz.localize(datetime_obj)
    
    # Calculate sun position using astral
    from astral.sun import azimuth, elevation
    
    sun_azimuth = azimuth(city.observer, datetime_obj)
    sun_elevation = elevation(city.observer, datetime_obj)
    
    return sun_azimuth, sun_elevation

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
