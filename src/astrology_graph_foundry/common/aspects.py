from __future__ import annotations
from typing import Any
from .constants import ASPECTS, DEFAULT_ORBS, MAJOR_ASPECTS, LUMINARIES, ANGLES, OUTER_PLANETS, POINTS
from .geometry import angular_distance, signed_delta
from .io import clean_body_name

def orb_allowed(a: str, b: str, aspect_name: str) -> float:
    base=DEFAULT_ORBS[aspect_name]
    names={clean_body_name(a), clean_body_name(b)}
    if names & LUMINARIES: base+=1.0
    if names & ANGLES: base+=0.5
    if names <= OUTER_PLANETS: base-=1.0
    if names & POINTS: base-=1.0
    return max(base,1.0)

def strength_label(orb: float) -> str:
    if orb <= .25: return "exact / ultra-partile"
    if orb <= .5: return "partile / extremely tight"
    if orb <= 1: return "very tight"
    if orb <= 2: return "tight"
    if orb <= 4: return "moderate"
    return "wide"

def find_aspect(a: str, lon_a: float, b: str, lon_b: float, include_minor: bool=True) -> dict[str, Any] | None:
    dist=angular_distance(lon_a, lon_b)
    best=None
    for name, exact_angle in ASPECTS.items():
        if not include_minor and name not in MAJOR_ASPECTS: continue
        orb=abs(dist-exact_angle)
        if orb <= orb_allowed(a,b,name):
            row={"aspect":name,"exact_angle":exact_angle,"distance":dist,"orb":orb,"major":name in MAJOR_ASPECTS,"strength":strength_label(orb),"applying_delta":signed_delta(lon_a,lon_b)}
            if best is None or row["orb"] < best["orb"]: best=row
    return best

def relevance_score(transit_body: str, natal_target: str, aspect: dict[str, Any]) -> float:
    score=max(0,10-aspect["orb"]*2)
    if aspect["major"]: score+=5
    if natal_target in {"nSun","nMoon"}: score+=4
    if transit_body in {"Sun","Moon"}: score+=2
    if natal_target in {"nASC","nDSC","nMC","nIC"}: score+=4
    if natal_target in {"nMercury","nVenus","nMars"}: score+=3
    if transit_body in {"Mercury","Venus","Mars"}: score+=2
    if transit_body in {"Saturn","Uranus","Neptune","Pluto"}: score+=4
    if transit_body=="Jupiter": score+=3
    return round(score,3)

def all_aspects(bodies_a: dict[str, dict[str, Any]], bodies_b: dict[str, dict[str, Any]], label_a: str="A", label_b: str="B", include_minor: bool=True) -> list[dict[str, Any]]:
    rows=[]
    idx=1
    for key_a, body_a in bodies_a.items():
        for key_b, body_b in bodies_b.items():
            if bodies_a is bodies_b and key_a == key_b: continue
            asp=find_aspect(key_a, float(body_a["lon"]), key_b, float(body_b["lon"]), include_minor)
            if asp:
                rows.append({"id":f"asp_{idx:04d}","source_label":label_a,"source_body":clean_body_name(key_a),"target_label":label_b,"target_body":clean_body_name(key_b),**asp,"weight":relevance_score(clean_body_name(key_a),key_b,asp)})
                idx+=1
    rows.sort(key=lambda r:(-r["weight"], r["orb"]))
    return rows
