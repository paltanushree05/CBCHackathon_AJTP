# engine/feasibility.py
from datetime import datetime, timedelta

DATE = "2026-04-25"

def parse_time(t):
    return datetime.fromisoformat(f"{DATE}T{t}")

def is_feasible(driver, pantry, donation, travel_seconds):
    now          = datetime.now()
    arrival      = now + timedelta(seconds=travel_seconds)
    pantry_open  = parse_time(pantry["open"])   # from CSV
    pantry_close = parse_time(pantry["close"])  # from CSV
    driver_end   = parse_time(driver["avail_end"])
    expiry       = datetime.fromisoformat(donation["expiry"])

    if arrival < pantry_open:                                              return False
    if arrival > pantry_close:                                             return False
    if arrival > driver_end:                                               return False
    if arrival > expiry:                                                   return False
    if driver["current_load"] + donation["quantity"] > driver["capacity"]: return False

    return True