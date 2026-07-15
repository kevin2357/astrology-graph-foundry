from __future__ import annotations
import logging
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo
from astrology_graph_foundry.common.aspects import all_aspects
from astrology_graph_foundry.common.constants import SIGN_RULERS_MODERN, SIGN_RULERS_TRADITIONAL
from astrology_graph_foundry.common.geometry import decimal_to_dms, format_zodiac, house_for_lon, normalize, deg_to_sign
from .models import BirthData, ProviderConfig

logger = logging.getLogger(__name__)

ELEMENTS = {"Aries":"Fire","Leo":"Fire","Sagittarius":"Fire","Taurus":"Earth","Virgo":"Earth","Capricorn":"Earth","Gemini":"Air","Libra":"Air","Aquarius":"Air","Cancer":"Water","Scorpio":"Water","Pisces":"Water"}
EXALTATIONS = {"Sun":"Aries","Moon":"Taurus","Mercury":"Virgo","Venus":"Pisces","Mars":"Capricorn","Jupiter":"Cancer","Saturn":"Libra"}
TRIPLICITIES = {"Fire":{"day":"Sun","night":"Jupiter"},"Earth":{"day":"Venus","night":"Moon"},"Air":{"day":"Saturn","night":"Mercury"},"Water":{"day":"Venus","night":"Mars"}}

def _unwrap_calc_result(result: Any) -> tuple | list:
    xx = result[0] if isinstance(result, tuple) and len(result) == 2 and isinstance(result[0], (list, tuple)) else result
    while isinstance(xx, (tuple, list)) and xx and isinstance(xx[0], (tuple, list)):
        xx = xx[0]
    return xx

def datetime_to_jd_ut(swe: Any, dt: datetime) -> tuple[float, datetime]:
    utc = dt.astimezone(ZoneInfo("UTC"))
    hour = utc.hour + utc.minute / 60 + utc.second / 3600
    return swe.julday(utc.year, utc.month, utc.day, hour), utc

def planet_position(swe: Any, jd_ut: float, swe_id: int, flags: int | None = None) -> dict[str, Any]:
    flags = flags if flags is not None else (swe.FLG_SWIEPH | swe.FLG_SPEED)
    xx = _unwrap_calc_result(swe.calc_ut(jd_ut, swe_id, flags))
    lon = normalize(float(xx[0]))
    lat = float(xx[1]) if len(xx) > 1 else None
    speed = float(xx[3]) if len(xx) > 3 else None
    return {"lon": lon, "lat": lat, "speed_lon": speed, "retrograde": bool(speed is not None and speed < 0), "pretty": format_zodiac(lon), "absolute_dms": decimal_to_dms(lon)}

def safe_planet_position(swe: Any, jd_ut: float, swe_id: int, flags: int | None = None) -> tuple[dict[str, Any] | None, str | None]:
    try:
        return planet_position(swe, jd_ut, swe_id, flags), None
    except Exception as exc:
        return None, str(exc)

def base_body_map(swe: Any) -> dict[str, int]:
    return {"Sun":swe.SUN,"Moon":swe.MOON,"Mercury":swe.MERCURY,"Venus":swe.VENUS,"Mars":swe.MARS,"Jupiter":swe.JUPITER,"Saturn":swe.SATURN,"Uranus":swe.URANUS,"Neptune":swe.NEPTUNE,"Pluto":swe.PLUTO,"True Node":swe.TRUE_NODE,"Mean Node":swe.MEAN_NODE}

def active_body_map(swe: Any, jd_ut: float | None = None, config: ProviderConfig | None = None) -> tuple[dict[str, int], list[dict[str, Any]]]:
    config = config or ProviderConfig()
    bodies = base_body_map(swe)
    skipped = []
    optional = {}
    if config.include_optional_points and hasattr(swe, "CHIRON"):
        optional["Chiron"] = swe.CHIRON
    if config.include_asteroids:
        for name in ("CERES", "PALLAS", "JUNO", "VESTA"):
            if hasattr(swe, name):
                optional[name.title()] = getattr(swe, name)
        for asteroid_id in config.asteroid_ids:
            optional[f"Asteroid {asteroid_id}"] = int(asteroid_id)
    if jd_ut is None:
        bodies.update(optional)
        return bodies, skipped
    for name, swe_id in optional.items():
        _, error = safe_planet_position(swe, jd_ut, swe_id)
        if error:
            skipped.append({"name": name, "swe_id": swe_id, "reason": error, "note": "Optional body skipped; missing Swiss Ephemeris file or unsupported object."})
        else:
            bodies[name] = swe_id
    return bodies, skipped

def house_data(swe: Any, jd_ut: float, lat: float, lon: float, house_system: str = "P") -> dict[str, Any]:
    cusps_raw, ascmc = swe.houses_ex(jd_ut, lat, lon, house_system.encode("ascii"))
    cusps_raw = list(cusps_raw)
    cusps = cusps_raw[1:] if len(cusps_raw) == 13 and abs(float(cusps_raw[0])) < 1e-9 else cusps_raw[:12]
    cusps = [normalize(float(x)) for x in cusps]
    asc = normalize(float(ascmc[0])); mc = normalize(float(ascmc[1]))
    closest_index = min(range(12), key=lambda i: abs((cusps[i] - asc + 180) % 360 - 180))
    if closest_index != 0:
        cusps = cusps[closest_index:] + cusps[:closest_index]
    return {"cusps": cusps, "ASC": asc, "DSC": normalize(asc + 180), "MC": mc, "IC": normalize(mc + 180), "Vertex": normalize(float(ascmc[3])) if len(ascmc) > 3 else None}

def is_day_chart(sun_house: int | None) -> bool:
    return sun_house in {7, 8, 9, 10, 11, 12}

def part_of_fortune(day_birth: bool, asc: float, sun: float, moon: float) -> float:
    return normalize(asc + moon - sun) if day_birth else normalize(asc + sun - moon)

def lot(asc: float, a: float, b: float, day_birth: bool) -> float:
    return normalize(asc + a - b) if day_birth else normalize(asc + b - a)

def house_rulers(cusps: list[float], modern: bool = False) -> dict[int, dict[str, Any]]:
    table = SIGN_RULERS_MODERN if modern else SIGN_RULERS_TRADITIONAL
    out = {}
    for i, cusp in enumerate(cusps, 1):
        sign = deg_to_sign(cusp)["sign"]
        out[i] = {"cusp_lon": cusp, "cusp_pretty": format_zodiac(cusp), "cusp_sign": sign, "ruler": table[sign]}
    return out

def dignity_for(body: str, sign: str, day_birth: bool) -> dict[str, Any]:
    from astrology_graph_foundry.common.constants import SIGNS
    opposite = SIGNS[(SIGNS.index(sign) + 6) % 12]
    elem = ELEMENTS.get(sign)
    trip = TRIPLICITIES.get(elem, {})
    trip_ruler = trip.get("day" if day_birth else "night")
    return {"sign": sign, "domicile_traditional": SIGN_RULERS_TRADITIONAL.get(sign) == body, "domicile_modern": SIGN_RULERS_MODERN.get(sign) == body, "exaltation": EXALTATIONS.get(body) == sign, "detriment_traditional": SIGN_RULERS_TRADITIONAL.get(opposite) == body, "fall": EXALTATIONS.get(body) == opposite, "triplicity_element": elem, "triplicity_ruler": trip_ruler, "is_triplicity_ruler": trip_ruler == body, "note": "Lightweight dignity model; terms/faces can be added later."}

def antiscia(lon: float) -> dict[str, Any]:
    anti = normalize(180 - lon)
    contra = normalize(360 - anti)
    return {"antiscia_lon": anti, "antiscia_pretty": format_zodiac(anti), "contra_antiscia_lon": contra, "contra_antiscia_pretty": format_zodiac(contra)}

def harmonic_positions(lon: float, numbers: tuple[int, ...]) -> dict[str, Any]:
    return {str(n): {"lon": normalize(lon * n), "pretty": format_zodiac(normalize(lon * n))} for n in numbers}

def declination_position(swe: Any, jd_ut: float, swe_id: int) -> dict[str, Any] | None:
    pos, err = safe_planet_position(swe, jd_ut, swe_id, swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_EQUATORIAL)
    if err or pos is None:
        return None
    return {"right_ascension": pos["lon"], "declination": pos["lat"], "declination_pretty": None if pos["lat"] is None else f"{pos['lat']:.5f}°"}

def declination_aspects(bodies: dict[str, dict[str, Any]], orb: float = 1.0) -> list[dict[str, Any]]:
    rows = []
    keys = [k for k, v in bodies.items() if v.get("declination") is not None]
    for i, a in enumerate(keys):
        for b in keys[i+1:]:
            da = bodies[a]["declination"]; db = bodies[b]["declination"]
            if abs(da - db) <= orb:
                rows.append({"a": a, "b": b, "type": "parallel", "orb": abs(da - db)})
            if abs(da + db) <= orb:
                rows.append({"a": a, "b": b, "type": "contra-parallel", "orb": abs(da + db)})
    return sorted(rows, key=lambda r: r["orb"])

def fixed_stars(swe: Any, jd_ut: float, names: tuple[str, ...]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    found, skipped = [], []
    for name in names:
        try:
            result = swe.fixstar2_ut(name, jd_ut)
            xx = result[0] if isinstance(result, tuple) else result
            star_name = result[1] if isinstance(result, tuple) and len(result) > 1 else name
            lon = normalize(float(xx[0]))
            found.append({"name": star_name, "lon": lon, "lat": float(xx[1]) if len(xx) > 1 else None, "pretty": format_zodiac(lon)})
        except Exception as exc:
            skipped.append({"name": name, "reason": str(exc)})
    return found, skipped

def build_live_natal_chart(birth: BirthData, config: ProviderConfig | None = None) -> dict[str, Any]:
    logger.info("Building live natal chart for %s", birth.name)
    try:
        import swisseph as swe
    except ImportError as exc:
        raise ImportError("Live natal computation requires pyswisseph (`pip install pyswisseph`).") from exc
    config = config or ProviderConfig()
    swe.set_ephe_path(config.ephe_path)
    birth_local_dt = datetime.fromisoformat(birth.birth_local).replace(tzinfo=ZoneInfo(birth.birth_timezone))
    birth_jd_ut, birth_utc_dt = datetime_to_jd_ut(swe, birth_local_dt)
    houses = house_data(swe, birth_jd_ut, birth.birth_lat, birth.birth_lon, config.house_system)
    active_bodies, skipped_optional = active_body_map(swe, birth_jd_ut, config)
    logger.info("Live natal active bodies=%d skipped_optional=%d", len(active_bodies), len(skipped_optional))
    natal = {}
    for name, swe_id in active_bodies.items():
        pos, err = safe_planet_position(swe, birth_jd_ut, swe_id)
        if err or pos is None:
            logger.warning("Skipping natal body %s: %s", name, err or "unknown calculation failure")
            skipped_optional.append({"name": name, "swe_id": swe_id, "reason": err or "unknown calculation failure"})
            continue
        body = {"name": f"n{name}", "lon": pos["lon"], "lat": pos["lat"], "speed_lon": pos["speed_lon"], "retrograde": pos["retrograde"], "house": house_for_lon(pos["lon"], houses["cusps"]), "pretty": pos["pretty"], "absolute_dms": pos["absolute_dms"], "type": "planet_or_point"}
        if config.include_declinations:
            dec = declination_position(swe, birth_jd_ut, swe_id)
            if dec:
                body.update(dec)
        natal[f"n{name}"] = body
    for angle_name in ["ASC", "DSC", "MC", "IC"]:
        natal[f"n{angle_name}"] = {"name": f"n{angle_name}", "lon": houses[angle_name], "lat": None, "speed_lon": None, "retrograde": False, "house": "-", "pretty": format_zodiac(houses[angle_name]), "absolute_dms": decimal_to_dms(houses[angle_name]), "type": "angle"}
    day_birth = is_day_chart(natal["nSun"]["house"])
    pof_lon = part_of_fortune(day_birth, houses["ASC"], natal["nSun"]["lon"], natal["nMoon"]["lon"])
    natal["nPart of Fortune"] = {"name":"nPart of Fortune","lon":pof_lon,"lat":None,"speed_lon":None,"retrograde":False,"house":house_for_lon(pof_lon,houses["cusps"]),"pretty":format_zodiac(pof_lon),"absolute_dms":decimal_to_dms(pof_lon),"type":"calculated_point"}
    if houses.get("Vertex") is not None:
        vlon = houses["Vertex"]
        natal["nVertex"] = {"name":"nVertex","lon":vlon,"lat":None,"speed_lon":None,"retrograde":False,"house":house_for_lon(vlon,houses["cusps"]),"pretty":format_zodiac(vlon),"absolute_dms":decimal_to_dms(vlon),"type":"angle_point"}
    if config.include_dignities:
        for key, body in natal.items():
            clean = key[1:] if key.startswith("n") else key
            if body.get("type") == "planet_or_point":
                body["dignity"] = dignity_for(clean, deg_to_sign(body["lon"])["sign"], day_birth)
    if config.include_antiscia:
        for body in natal.values():
            body["antiscia"] = antiscia(body["lon"])
    if config.include_harmonics:
        for body in natal.values():
            body["harmonics"] = harmonic_positions(body["lon"], config.harmonic_numbers)
    fixed_star_records, skipped_stars = fixed_stars(swe, birth_jd_ut, config.fixed_star_names) if config.include_fixed_stars else ([], [])
    natal_planets = {k:v for k,v in natal.items() if v["type"] == "planet_or_point"}
    natal_angles = {k:v for k,v in natal.items() if v["type"] in {"angle", "angle_point"}}
    natal_points = {k:v for k,v in natal.items() if v["type"] == "calculated_point"}
    trad_rulers = house_rulers(houses["cusps"], False); modern_rulers = house_rulers(houses["cusps"], True)
    lots = {"Fortune": {"lon": pof_lon, "pretty": format_zodiac(pof_lon), "house": house_for_lon(pof_lon, houses["cusps"])}, "Spirit": {"lon": lot(houses["ASC"], natal["nSun"]["lon"], natal["nMoon"]["lon"], day_birth)}}
    lots["Spirit"].update({"pretty": format_zodiac(lots["Spirit"]["lon"]), "house": house_for_lon(lots["Spirit"]["lon"], houses["cusps"])})
    decl_bodies = {k: {"declination": v.get("declination")} for k, v in natal.items() if v.get("declination") is not None}
    logger.info("Live natal chart complete for %s: bodies=%d skipped_optional=%d fixed_stars=%d", birth.name, len(natal), len(skipped_optional), len(fixed_star_records))
    return {"type":"natal_chart","person":birth.name,"birth_local":birth.birth_local,"birth_timezone":birth.birth_timezone,"birth_utc":birth_utc_dt.isoformat(),"birth_lat":birth.birth_lat,"birth_lon":birth.birth_lon,"birth_location_label":birth.birth_location_label,"jd_ut":birth_jd_ut,"house_system":config.house_system,"calculation_options":{"include_declinations":config.include_declinations,"include_dignities":config.include_dignities,"include_sect":config.include_sect,"include_antiscia":config.include_antiscia,"include_harmonics":config.include_harmonics,"harmonic_numbers":list(config.harmonic_numbers),"include_optional_points":config.include_optional_points,"include_asteroids":config.include_asteroids,"include_fixed_stars":config.include_fixed_stars},"calculation_warnings":{"skipped_optional_bodies":skipped_optional,"skipped_fixed_stars":skipped_stars},"sect":{"is_day_chart":day_birth,"sect_light":"Sun" if day_birth else "Moon","out_of_sect_light":"Moon" if day_birth else "Sun"},"houses":{str(i):{"lon":houses["cusps"][i-1],"pretty":format_zodiac(houses["cusps"][i-1]),"traditional_ruler":trad_rulers[i]["ruler"],"modern_ruler":modern_rulers[i]["ruler"]} for i in range(1,13)},"angles":{k:houses[k] for k in ["ASC","DSC","MC","IC"]},"bodies":natal,"lots":lots,"fixed_stars":fixed_star_records,"declination_aspects":declination_aspects(decl_bodies) if config.include_declinations else [],"natal_planet_aspects":all_aspects(natal_planets,natal_planets,"natal","natal",include_minor=config.include_minor),"natal_planet_angle_aspects":all_aspects(natal_planets,natal_angles,"natal","natal",include_minor=config.include_minor),"natal_planet_point_aspects":all_aspects(natal_planets,natal_points,"natal","natal",include_minor=config.include_minor)}
