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

def get_sun_position(dt):
    """Calculate sun position for Dar es Salaam"""
    # Dar es Salaam coordinates
    lat = -6.7924
    lon = 39.2083
    
    # Convert to Julian day
    a = (14 - dt.month) // 12
    y = dt.year - a
    m = dt.month + 12 * a - 3
    jd = dt.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 + 1721119
    
    # Add time of day
    jd += (dt.hour - 12) / 24.0 + dt.minute / 1440.0 + dt.second / 86400.0
    
    # Calculate sun position
    n = jd - 2451545.0
    L = (280.460 + 0.9856474 * n) % 360
    g = math.radians((357.528 + 0.9856003 * n) % 360)
    lambda_sun = math.radians(L + 1.915 * math.sin(g) + 0.020 * math.sin(2 * g))
    
    # Declination
    delta = math.asin(math.sin(math.radians(23.439)) * math.sin(lambda_sun))
    
    # Hour angle
    alpha = math.radians((280.147 + 0.9856474 * n) % 360)
    H = alpha + math.radians(lon) - lambda_sun
    
    # Convert to local coordinates
    lat_rad = math.radians(lat)
    elevation = math.asin(math.sin(lat_rad) * math.sin(delta) + 
                         math.cos(lat_rad) * math.cos(delta) * math.cos(H))
    
    azimuth = math.atan2(math.sin(H), 
                        math.cos(H) * math.sin(lat_rad) - 
                        math.tan(delta) * math.cos(lat_rad))
    
    azimuth = math.degrees(azimuth)
    elevation = math.degrees(elevation)
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
