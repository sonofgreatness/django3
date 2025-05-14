import logging
import csv
import time
from collections import namedtuple
from math import radians, cos, sin, sqrt, atan2

from geopy.geocoders import Nominatim
from api.models import Trip
# Configure logger
logger = logging.getLogger(__name__)

GasStation = namedtuple("GasStation", ["name", "lat", "lon", "price", "address", "state"])

# Setup Nominatim geocoder
geolocator = Nominatim(user_agent="SimphiweGasApp/1.0 (simphiweiq@gmail.com)", timeout=40)

def geocode_address(address, state):
    try:
        location = geolocator.geocode(f"{address}, {state}, USA")
        if location:
            print(f"Geocoded: {address}, {state} => {location.latitude}, {location.longitude}")
            return location.latitude, location.longitude
    except Exception as e:
        print(f"Geocoding failed for {address}, {state}: {e}")
    return None, None


def load_gas_stations(csv_path):
    stations = []
    updated_rows = []

    with open(csv_path, newline='', encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ["Latitude", "Longitude"] if "Latitude" not in reader.fieldnames else reader.fieldnames
        
        for row in reader:
            name = row['Truckstop Name']
            address = row['Address']
            state = row['State']
            price = float(row['Retail Price'])

            # Use existing lat/lon if available
            lat = row.get("Latitude")
            lon = row.get("Longitude")

            if not lat or not lon:
                lat, lon = geocode_address(address, state)
                row["Latitude"] = lat
                row["Longitude"] = lon
                time.sleep(1)  # polite rate limit

            if lat and lon:
                stations.append(GasStation(
                    name=name,
                    lat=float(lat),
                    lon=float(lon),
                    price=price,
                    address=address,
                    state=state
                ))
            updated_rows.append(row)

    # Save back the updated CSV with lat/lon included
    with open(csv_path, "w", newline='', encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)

    return stations

def get_stations(csv_path):
    stations = []
    logger.info("get stations called")
    with open(csv_path, newline='', encoding="utf-8") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            lat = row.get("Latitude")
            lon = row.get("Longitude")

            if not lat or not lon:
                continue  # Skip invalid rows

            try:
                station = GasStation(
                    name=row['Truckstop Name'],
                    lat=float(lat),
                    lon=float(lon),
                    price=float(row['Retail Price']),
                    address=row['Address'],
                    state=row['State']
                )
                stations.append(station)
            except (ValueError, KeyError) as e:
                logger.warning(f"Skipping row due to error: {e}")

    logger.info(f"{len(stations)} valid gas stations loaded from {csv_path}")
    return stations




def haversine_distance(lat1, lon1, lat2, lon2):
    R = 3958.8  # Radius of Earth in miles
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c


def process_trip_routes(trip_id, csv_path, max_range=500):
    trip = Trip.objects.get(id=trip_id)
    stations = get_stations(csv_path)

    total_distance = haversine_distance(
        trip.start_lat, trip.start_lng, trip.end_lat, trip.end_lng
    )

    num_refuels = int(total_distance // max_range)
    
    refueling_points = []
    interval_distance = total_distance / (num_refuels + 1)
    logger.info(f"num_refuels , {num_refuels} interval_distance : {interval_distance}")
    
    for i in range(1, num_refuels + 1):
        lat = trip.start_lat + (trip.end_lat - trip.start_lat) * (i / (num_refuels + 1))
        lon = trip.start_lng + (trip.end_lng - trip.start_lng) * (i / (num_refuels + 1))

        nearby = [
            s for s in stations if haversine_distance(lat, lon, s.lat, s.lon) < 3000
        ]
        logger.info(f"nearby => {nearby}")
        logger.info(f"loop lat => {lat} ,  long => {lon}")
        if nearby:
            cheapest = min(nearby, key=lambda s: s.price)
            refueling_points.append({
                'name': cheapest.name,
                'lat': cheapest.lat,
                'lon': cheapest.lon,
                'price': cheapest.price
            })

    return {
        'from': trip.start_location,
        'to': trip.end_location,
        'distance_miles': round(total_distance, 2),
        'refueling_points': refueling_points
    }
