import math
from datetime import datetime
import pytz

def calculate_bearing(start_lat, start_lon, end_lat, end_lon):
    """Calculate bearing between two points"""
    start_lat, start_lon = math.radians(start_lat), math.radians(start_lon)
    end_lat, end_lon = math.radians(end_lat), math.radians(end_lon)
    dlon = end_lon - start_lon
    
    x = math.sin(dlon) * math.cos(end_lat)
    y = math.cos(start_lat) * math.sin(end_lat) - math.sin(start_lat) * math.cos(end_lat) * math.cos(dlon)
    
    bearing = math.atan2(x, y)
    bearing = math.degrees(bearing)
    bearing = (bearing + 360) % 360
    
    return bearing

def julian_day(dt):
    """Calculate Julian day number"""
    a = (14 - dt.month) // 12
    y = dt.year + 4800 - a
    m = dt.month + 12 * a - 3
    
    return dt.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045

def get_sun_position(dt, lat, lon):
    """Calculate sun position (azimuth and elevation) for given time and location"""
    # Convert to UTC
    utc_dt = dt.astimezone(pytz.UTC)
    
    # Julian day
    jd = julian_day(utc_dt)
    
    # Time in decimal hours
    time_decimal = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
    
    # Julian century
    jc = (jd + time_decimal / 24.0 - 2451545.0) / 36525.0
    
    # Solar coordinates
    geom_mean_long_sun = (280.46646 + jc * (36000.76983 + jc * 0.0003032)) % 360
    geom_mean_anom_sun = 357.52911 + jc * (35999.05029 - 0.0001537 * jc)
    
    eccent_earth_orbit = 0.016708634 - jc * (0.000042037 + 0.0000001267 * jc)
    
    sun_eq_of_ctr = math.sin(math.radians(geom_mean_anom_sun)) * (1.914602 - jc * (0.004817 + 0.000014 * jc)) + \
                    math.sin(math.radians(2 * geom_mean_anom_sun)) * (0.019993 - 0.000101 * jc) + \
                    math.sin(math.radians(3 * geom_mean_anom_sun)) * 0.000289
    
    sun_true_long = geom_mean_long_sun + sun_eq_of_ctr
    
    mean_obliq_ecliptic = 23 + (26 + ((21.448 - jc * (46.815 + jc * (0.00059 - jc * 0.001813)))) / 60) / 60
    obliq_corr = mean_obliq_ecliptic + 0.00256 * math.cos(math.radians(125.04 - 1934.136 * jc))
    
    sun_declin = math.degrees(math.asin(math.sin(math.radians(obliq_corr)) * math.sin(math.radians(sun_true_long))))
    
    var_y = math.tan(math.radians(obliq_corr / 2)) ** 2
    eq_of_time = 4 * math.degrees(var_y * math.sin(2 * math.radians(geom_mean_long_sun)) - 
                                  2 * eccent_earth_orbit * math.sin(math.radians(geom_mean_anom_sun)) +
                                  4 * eccent_earth_orbit * var_y * math.sin(math.radians(geom_mean_anom_sun)) * 
                                  math.cos(2 * math.radians(geom_mean_long_sun)) -
                                  0.5 * var_y * var_y * math.sin(4 * math.radians(geom_mean_long_sun)) -
                                  1.25 * eccent_earth_orbit * eccent_earth_orbit * math.sin(2 * math.radians(geom_mean_anom_sun)))
    
    # Local solar time
    true_solar_time = ((time_decimal * 60 + eq_of_time + 4 * lon) % 1440) / 4
    
    # Hour angle
    if true_solar_time < 0:
        hour_angle = true_solar_time + 180
    else:
        hour_angle = true_solar_time - 180
    
    # Solar zenith angle
    lat_rad = math.radians(lat)
    declin_rad = math.radians(sun_declin)
    hour_angle_rad = math.radians(hour_angle)
    
    zenith_angle = math.degrees(math.acos(math.sin(lat_rad) * math.sin(declin_rad) + 
                                         math.cos(lat_rad) * math.cos(declin_rad) * math.cos(hour_angle_rad)))
    
    # Solar elevation
    elevation = 90 - zenith_angle
    
    # Solar azimuth
    if hour_angle > 0:
        azimuth = (math.degrees(math.acos(((math.sin(lat_rad) * math.cos(math.radians(zenith_angle))) - 
                                          math.sin(declin_rad)) / (math.cos(lat_rad) * math.sin(math.radians(zenith_angle))))) + 180) % 360
    else:
        azimuth = (540 - math.degrees(math.acos(((math.sin(lat_rad) * math.cos(math.radians(zenith_angle))) - 
                                                math.sin(declin_rad)) / (math.cos(lat_rad) * math.sin(math.radians(zenith_angle)))))) % 360
    
    return azimuth, elevation

def determine_best_side(travel_dir: float, sun_azimuth: float):
    """Determine which side of the vehicle to sit on for shade"""
    # Calculate the relative angle of the sun to the direction of travel
    relative_angle = (sun_azimuth - travel_dir + 360) % 360
    
    # If sun is on the left side (90° to 270°), sit on the right
    # If sun is on the right side (270° to 90°), sit on the left
    if 90 <= relative_angle <= 270:
        return "right"
    else:
        return "left"