import math
from datetime import datetime

def berlin_daytime(daytime):
    # Berlin coordinates
    latitude = 52.52
    longitude = 13.41

    # Get current date
    current_date = datetime.now()
    day_of_year = current_date.timetuple().tm_yday

    # Calculate declination of the Sun
    declination = 23.45 * math.sin(math.radians((360/365) * (day_of_year - 81)))

    # Calculate equation of time
    b = 360 * (day_of_year - 81) / 365
    equation_of_time = 9.87 * math.sin(math.radians(2*b)) - 7.53 * math.cos(math.radians(b)) - 1.5 * math.sin(math.radians(b))

    # Calculate solar hour angle
    hour_angle = math.degrees(math.acos(-math.tan(math.radians(latitude)) * math.tan(math.radians(declination))))

    # Calculate sunrise and sunset times (in decimal hours)
    sunrise_time = 12 - hour_angle/15 - equation_of_time/60 + (15 - longitude)/15
    sunset_time = 12 + hour_angle/15 - equation_of_time/60 + (15 - longitude)/15

    # Convert to integer hours
    sunrise_hour = int(sunrise_time)
    sunset_hour = int(sunset_time)

    if daytime == "sunrise":
        return sunrise_hour
    if daytime == "sunset":
        return sunset_hour 
    return 0
