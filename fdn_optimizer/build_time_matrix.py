# engine/build_time_matrix.py
import requests
import os

def build_time_matrix(donations, pantries):
    # combine donor and pantry locations into one list
    locations = [d["location"] for d in donations] + \
                [[p["lat"], p["lng"]] for p in pantries]  # real lat/lng from CSV

    # ORS expects [lng, lat] not [lat, lng]
    coords = [[loc[1], loc[0]] for loc in locations]

    response = requests.post(
        "https://api.openrouteservice.org/v2/matrix/driving-car",
        headers={ "Authorization": os.getenv("ORS_API_KEY") },
        json={ "locations": coords }
    )

    data = response.json()
    return data["durations"]  # pairwise matrix in seconds