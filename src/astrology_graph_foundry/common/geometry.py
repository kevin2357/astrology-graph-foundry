from __future__ import annotations
from .constants import SIGNS

def normalize(deg: float) -> float:
    return float(deg) % 360.0

def angular_distance(lon1: float, lon2: float) -> float:
    diff=abs((float(lon1)-float(lon2))%360.0)
    return min(diff, 360.0-diff)

def signed_delta(from_lon: float, to_lon: float) -> float:
    return ((float(to_lon)-float(from_lon)+180.0)%360.0)-180.0

def midpoint(lon_a: float, lon_b: float) -> float:
    return normalize(float(lon_a)+signed_delta(lon_a,lon_b)/2.0)

def deg_to_sign(lon_deg: float) -> dict:
    lon=normalize(lon_deg)
    idx=int(lon//30)
    return {"lon": lon, "sign": SIGNS[idx], "sign_degree": lon%30.0, "sign_index": idx}

def format_zodiac(lon_deg: float) -> str:
    info=deg_to_sign(lon_deg)
    deg=int(info["sign_degree"])
    minutes_float=(info["sign_degree"]-deg)*60
    minutes=int(minutes_float)
    seconds=round((minutes_float-minutes)*60,1)
    return f"{info['sign']} {deg:02d}°{minutes:02d}'{seconds:04.1f}\\\""

def decimal_to_dms(lon_deg: float) -> str:
    lon=normalize(lon_deg)
    deg=int(lon)
    minutes_float=(lon-deg)*60
    minutes=int(minutes_float)
    seconds=round((minutes_float-minutes)*60,1)
    return f"{deg:03d}°{minutes:02d}'{seconds:04.1f}\\\""

def house_for_lon(lon: float, cusps: list[float]) -> int | None:
    lon=normalize(lon)
    for i in range(12):
        start=normalize(cusps[i])
        end=normalize(cusps[(i+1)%12])
        if start < end:
            if start <= lon < end: return i+1
        else:
            if lon >= start or lon < end: return i+1
    return None
