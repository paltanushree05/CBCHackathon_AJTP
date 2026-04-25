# engine/sort_edf.py
from datetime import datetime

def sort_by_edf(donations):
    return sorted(donations, key=lambda d: datetime.fromisoformat(d["expiry"]))

def sort_pantries_by_close(pantries):
    # pantries from CSV use "close" field directly
    return sorted(pantries, key=lambda p: p["close"])