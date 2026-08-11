from __future__ import annotations

import logging
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from astrology_graph_foundry.common.aspects import all_aspects
from astrology_graph_foundry.common.constants import SIGN_RULERS_MODERN, SIGN_RULERS_TRADITIONAL
from astrology_graph_foundry.common.geometry import decimal_to_dms, deg_to_sign, format_zodiac, house_for_lon, normalize

from .interval_evaluation import (
    IntervalProofProfile,
    _classify_longitude_relationship,
    evaluate_interval,
    evaluation_times,
)
from .models import BOUNDED_HOUSE_SYSTEMS, BirthData, BoundedBirthData, ProviderConfig
from .uncertainty_evidence import circular_range_from_unwrapped, evidence_record, transition_witnesses

logger = logging.getLogger(__name__)

ELEMENTS = {"Aries":"Fire","Leo":"Fire","Sagittarius":"Fire","Taurus":"Earth","Virgo":"Earth","Capricorn":"Earth","Gemini":"Air","Libra":"Air","Aquarius":"Air","Cancer":"Water","Scorpio":"Water","Pisces":"Water"}
EXALTATIONS = {"Sun":"Aries","Moon":"Taurus","Mercury":"Virgo","Venus":"Pisces","Mars":"Capricorn","Jupiter":"Cancer","Saturn":"Libra"}
TRIPLICITIES = {"Fire":{"day":"Sun","night":"Jupiter"},"Earth":{"day":"Venus","night":"Moon"},"Air":{"day":"Saturn","night":"Mercury"},"Water":{"day":"Venus","night":"Mars"}}

def _split_calc_result(result: Any) -> tuple[tuple | list, int | None]:
    returned_flags = None
    if isinstance(result, tuple) and len(result) == 2 and isinstance(result[0], (list, tuple)):
        xx, returned_flags = result
    else:
        xx = result
    while isinstance(xx, (tuple, list)) and xx and isinstance(xx[0], (tuple, list)):
        xx = xx[0]
    return xx, int(returned_flags) if returned_flags is not None else None

def ephemeris_flag(swe: Any, mode: str) -> int:
    return {"auto": swe.FLG_SWIEPH, "swiss": swe.FLG_SWIEPH, "moshier": swe.FLG_MOSEPH}[mode]

def ephemeris_name_from_flags(swe: Any, flags: int | None) -> str:
    if flags is None:
        return "unreported"
    for name, flag_name in (("jpl", "FLG_JPLEPH"), ("swiss", "FLG_SWIEPH"), ("moshier", "FLG_MOSEPH")):
        if flags & getattr(swe, flag_name):
            return name
    return "unreported"

def validate_ephemeris_mode(requested_mode: str, observed_modes: set[str]) -> None:
    if requested_mode in {"swiss", "moshier"} and observed_modes != {requested_mode}:
        raise RuntimeError(
            f"Requested ephemeris mode {requested_mode!r}, but Swiss Ephemeris returned "
            f"{sorted(observed_modes)!r}"
        )

def datetime_to_jd_ut(swe: Any, dt: datetime) -> tuple[float, datetime]:
    utc = dt.astimezone(ZoneInfo("UTC"))
    hour = utc.hour + utc.minute / 60 + utc.second / 3600
    return swe.julday(utc.year, utc.month, utc.day, hour), utc

def planet_position(swe: Any, jd_ut: float, swe_id: int, flags: int | None = None) -> dict[str, Any]:
    flags = flags if flags is not None else (swe.FLG_SWIEPH | swe.FLG_SPEED)
    xx, returned_flags = _split_calc_result(swe.calc_ut(jd_ut, swe_id, flags))
    lon = normalize(float(xx[0]))
    lat = float(xx[1]) if len(xx) > 1 else None
    speed = float(xx[3]) if len(xx) > 3 else None
    speed_lat = float(xx[4]) if len(xx) > 4 else None
    return {"lon": lon, "lat": lat, "speed_lon": speed, "speed_lat": speed_lat, "retrograde": bool(speed is not None and speed < 0), "pretty": format_zodiac(lon), "absolute_dms": decimal_to_dms(lon), "ephemeris_return_flags": returned_flags, "ephemeris_actual": ephemeris_name_from_flags(swe, returned_flags)}

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
        flags = ephemeris_flag(swe, config.ephemeris_mode) | swe.FLG_SPEED
        _, error = safe_planet_position(swe, jd_ut, swe_id, flags)
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
    if len(cusps) != 12:
        raise ValueError(f"house system {house_system!r} did not return twelve cusps")
    asc = normalize(float(ascmc[0])); mc = normalize(float(ascmc[1]))
    return {"cusps": cusps, "ASC": asc, "DSC": normalize(asc + 180), "MC": mc, "IC": normalize(mc + 180), "Vertex": normalize(float(ascmc[3])) if len(ascmc) > 3 else None}


def _unwrap_path(values: list[float]) -> list[float]:
    path = [values[0]]
    for value in values[1:]:
        path.append(path[-1] + ((value - path[-1] + 180.0) % 360.0 - 180.0))
    return path


def _frame_coordinate_evidence(
    key: str,
    values: list[float],
    speeds: list[float],
    times: list[float],
    factor: float,
) -> dict[str, Any]:
    path = _unwrap_path(values)
    padding = [
        max(abs(speeds[index]), abs(speeds[index + 1]))
        * (times[index + 1] - times[index])
        * factor
        for index in range(len(times) - 1)
    ]
    low = min(value - (padding[index - 1] if index else padding[0]) for index, value in enumerate(path))
    high = max(value + (padding[index - 1] if index else padding[0]) for index, value in enumerate(path))
    first = int((low + 1e-7) // 30)
    last = int((high - 1e-7) // 30)
    signs = sorted({index % 12 for index in range(first, last + 1)})
    sampled_signs = [int(value // 30) % 12 for value in values]
    return evidence_record(
        feature_key=f"terrestrial_frame:{key}",
        classification="invariant" if len(signs) == 1 else "variable",
        value_kind="terrestrial_ecliptic_longitude",
        possibilities=(str(index) for index in signs),
        prerequisite_refs=["provider:houses_ex2"],
        range_evidence=circular_range_from_unwrapped(low, high),
        transitions=transition_witnesses(sampled_signs, times, coordinate_unit="jd_ut"),
        availability="available",
    )


def evaluate_terrestrial_frame_interval(
    swe: Any,
    start_jd: float,
    end_jd: float,
    latitude: float,
    longitude: float,
    config: ProviderConfig,
    profile: IntervalProofProfile,
    position_evaluator: Any | None = None,
) -> dict[str, Any]:
    if config.house_system not in BOUNDED_HOUSE_SYSTEMS:
        return {"status": "unsupported", "house_system": config.house_system, "failures": [{"reason": "house_system_not_qualified_for_bounded_natal"}]}
    times = evaluation_times(start_jd, end_jd, profile.minimum_step_seconds)
    if len(times) > profile.maximum_evaluations:
        return {"status": "inconclusive", "house_system": config.house_system, "failures": [{"reason": "initial evaluation budget exceeded"}]}
    samples = []
    try:
        for time in times:
            cusps, ascmc, cusp_speeds, ascmc_speeds = swe.houses_ex2(
                time, latitude, longitude, config.house_system.encode("ascii")
            )
            if len(cusps) != 12:
                raise ValueError("provider did not return twelve cusps")
            positions = position_evaluator(time) if position_evaluator is not None else {}
            samples.append((list(cusps), list(ascmc), list(cusp_speeds), list(ascmc_speeds), positions))
    except Exception as exc:
        return {"status": "inconclusive", "house_system": config.house_system, "failures": [{"reason": f"provider_failure: {type(exc).__name__}: {exc}"}]}
    coordinates = {}
    for index in range(12):
        coordinates[f"cusp:{index + 1}"] = _frame_coordinate_evidence(
            f"cusp:{index + 1}",
            [float(sample[0][index]) % 360 for sample in samples],
            [float(sample[2][index]) for sample in samples],
            times,
            profile.speed_envelope_factor,
        )
    angle_sources = {"ASC": (1, 0, 1.0, 0.0), "DSC": (1, 0, 1.0, 180.0), "MC": (1, 1, 1.0, 0.0), "IC": (1, 1, 1.0, 180.0), "Vertex": (1, 3, 1.0, 0.0)}
    for name, (_, index, multiplier, offset) in angle_sources.items():
        coordinates[f"angle:{name}"] = _frame_coordinate_evidence(
            f"angle:{name}",
            [(float(sample[1][index]) * multiplier + offset) % 360 for sample in samples],
            [float(sample[3][index]) * multiplier for sample in samples],
            times,
            profile.speed_envelope_factor,
        )
    calculated_points = {}
    point_specs = {
            "Fortune": {
                "day": ("asc_plus_moon_minus_sun", 1.0, -1.0),
                "night": ("asc_plus_sun_minus_moon", -1.0, 1.0),
            },
            "Spirit": {
                "day": ("asc_plus_sun_minus_moon", -1.0, 1.0),
                "night": ("asc_plus_moon_minus_sun", 1.0, -1.0),
            },
    }
    can_calculate_points = position_evaluator is not None and config.include_sect and {"Sun", "Moon"}.issubset(samples[0][4])
    if can_calculate_points:
        sampled_sects = []
        for sample in samples:
            sun_house = house_for_lon(float(sample[4]["Sun"]["lon"]), [float(value) for value in sample[0]])
            sampled_sects.append("day" if is_day_chart(sun_house) else "night")
        for point_name, formulas in point_specs.items():
            values = []
            speeds = []
            formula_ids = []
            for sample, sect_value in zip(samples, sampled_sects):
                formula_id, moon_factor, sun_factor = formulas[sect_value]
                asc = float(sample[1][0])
                sun = float(sample[4]["Sun"]["lon"])
                moon = float(sample[4]["Moon"]["lon"])
                values.append(normalize(asc + moon_factor * moon + sun_factor * sun))
                speeds.append(
                    float(sample[3][0])
                    + moon_factor * float(sample[4]["Moon"]["speed_lon"])
                    + sun_factor * float(sample[4]["Sun"]["speed_lon"])
                )
                formula_ids.append(formula_id)
            branches = []
            branch_signs = set()
            start = 0
            while start < len(times):
                end = start
                while end + 1 < len(times) and formula_ids[end + 1] == formula_ids[start]:
                    end += 1
                branch_values = values[start : end + 1]
                branch_path = _unwrap_path(branch_values)
                if len(branch_path) == 1:
                    low = high = branch_path[0]
                else:
                    padding = [
                        max(abs(speeds[index]), abs(speeds[index + 1]))
                        * (times[index + 1] - times[index])
                        * profile.speed_envelope_factor
                        for index in range(start, end)
                    ]
                    low = min(value - (padding[index - 1] if index else padding[0]) for index, value in enumerate(branch_path))
                    high = max(value + (padding[index - 1] if index else padding[0]) for index, value in enumerate(branch_path))
                first_sign = int((low + 1e-7) // 30)
                last_sign = int((high - 1e-7) // 30)
                signs = sorted({index % 12 for index in range(first_sign, last_sign + 1)})
                branch_signs.update(signs)
                branches.append({
                    "formula_id": formula_ids[start],
                    "sect": sampled_sects[start],
                    "sample_index_start": start,
                    "sample_index_end": end,
                    "interval": {"start_jd": times[start], "end_jd": times[end], "boundary_policy": "inclusive"},
                    "longitude_range": circular_range_from_unwrapped(low, high),
                    "possible_sign_indexes": signs,
                })
                start = end + 1
            calculated_points[point_name] = {
                "feature_key": f"calculated_point:{point_name}",
                "classification": "invariant" if len(branch_signs) == 1 else "variable",
                "value_kind": "branched_calculated_point_longitude",
                "availability": "available",
                "possible_sign_indexes": sorted(branch_signs),
                "possible_formula_ids": sorted(set(formula_ids)),
                "branches": branches,
                "prerequisite_refs": ["terrestrial_frame:angle:ASC", "body:Sun", "body:Moon", "terrestrial_frame:sect"],
                "transition_witnesses": transition_witnesses(formula_ids, times, coordinate_unit="jd_ut"),
            }
    else:
        for point_name in point_specs:
            calculated_points[point_name] = evidence_record(
                feature_key=f"calculated_point:{point_name}",
                classification="unavailable",
                value_kind="branched_calculated_point_longitude",
                prerequisite_refs=["terrestrial_frame:angle:ASC", "body:Sun", "body:Moon", "terrestrial_frame:sect"],
                availability="disabled" if not config.include_sect else "prerequisite_unavailable",
                status_reason="sect disabled by configuration" if not config.include_sect else "Sun or Moon coordinate unavailable",
            )
    cusp_semantics = {}
    for house_number in range(1, 13):
        coordinate = coordinates[f"cusp:{house_number}"]
        sign_indexes = [int(value) for value in coordinate["possibilities"]["values"]]
        sign_names = [deg_to_sign(index * 30.0)["sign"] for index in sign_indexes]
        cusp_semantics[str(house_number)] = {
            "sign": evidence_record(
                feature_key=f"terrestrial_frame:cusp:{house_number}:sign",
                classification="invariant" if len(sign_names) == 1 else "variable",
                value_kind="zodiac_sign",
                possibilities=sign_names,
                prerequisite_refs=[f"terrestrial_frame:cusp:{house_number}"],
                transitions=coordinate["transition_witnesses"],
                availability="available",
            ),
            "traditional_ruler": evidence_record(
                feature_key=f"terrestrial_frame:cusp:{house_number}:traditional_ruler",
                classification="invariant" if len(sign_names) == 1 else "variable",
                value_kind="traditional_house_ruler",
                possibilities=(SIGN_RULERS_TRADITIONAL[sign] for sign in sign_names),
                prerequisite_refs=[f"terrestrial_frame:cusp:{house_number}:sign"],
                availability="available",
            ),
            "modern_ruler": evidence_record(
                feature_key=f"terrestrial_frame:cusp:{house_number}:modern_ruler",
                classification="invariant" if len(sign_names) == 1 else "variable",
                value_kind="modern_house_ruler",
                possibilities=(SIGN_RULERS_MODERN[sign] for sign in sign_names),
                prerequisite_refs=[f"terrestrial_frame:cusp:{house_number}:sign"],
                availability="available",
            ),
        }
    memberships = {}
    angle_relationships = []
    calculated_point_relationships = []
    if position_evaluator is not None:
        node_names = []
        first_positions = samples[0][4]
        for body_name in first_positions:
            node_names.append((f"body:{body_name}", body_name, lambda row, n=body_name: float(row[n]["lon"]), lambda row, n=body_name: float(row[n]["speed_lon"])))
            if config.include_antiscia:
                node_names.extend([
                    (f"transform:{body_name}:antiscia", f"{body_name} antiscia", lambda row, n=body_name: normalize(180.0 - float(row[n]["lon"])), lambda row, n=body_name: -float(row[n]["speed_lon"])),
                    (f"transform:{body_name}:contra_antiscia", f"{body_name} contra antiscia", lambda row, n=body_name: normalize(180.0 + float(row[n]["lon"])), lambda row, n=body_name: float(row[n]["speed_lon"])),
                ])
            if config.include_harmonics:
                for number in config.harmonic_numbers:
                    node_names.append((f"transform:{body_name}:harmonic:{number}", f"{body_name} harmonic {number}", lambda row, n=body_name, k=number: normalize(float(row[n]["lon"]) * k), lambda row, n=body_name, k=number: float(row[n]["speed_lon"]) * k))
        node_names.append(("angle:Vertex", "Vertex", lambda row: 0.0, lambda row: 0.0))
        for point_name, point_evidence in calculated_points.items():
            if point_evidence.get("availability") != "available":
                continue
            node_names.append((f"calculated_point:{point_name}", point_name, None, None))
        for node_key, display_name, lon_getter, speed_getter in node_names:
            def node_lon(sample_index):
                sample = samples[sample_index]
                if node_key == "angle:Vertex":
                    return float(sample[1][3]) % 360
                if node_key.startswith("calculated_point:"):
                    point = node_key.split(":", 1)[1]
                    day = sampled_sects[sample_index] == "day"
                    return (
                        part_of_fortune(day, float(sample[1][0]), float(sample[4]["Sun"]["lon"]), float(sample[4]["Moon"]["lon"]))
                        if point == "Fortune"
                        else lot(float(sample[1][0]), float(sample[4]["Sun"]["lon"]), float(sample[4]["Moon"]["lon"]), day)
                    )
                return lon_getter(sample[4])

            def node_speed(sample_index):
                sample = samples[sample_index]
                if node_key == "angle:Vertex":
                    return float(sample[3][3])
                if node_key.startswith("calculated_point:"):
                    point = node_key.split(":", 1)[1]
                    factors = point_specs[point][sampled_sects[sample_index]]
                    return float(sample[3][0]) + factors[1] * float(sample[4]["Moon"]["speed_lon"]) + factors[2] * float(sample[4]["Sun"]["speed_lon"])
                return speed_getter(sample[4])

            observed = []
            possible = set()
            safety_houses = set()
            for sample_index, sample in enumerate(samples):
                body_lon = node_lon(sample_index)
                house = house_for_lon(body_lon, [float(value) for value in sample[0]])
                observed.append(house)
                if house is not None:
                    possible.add(house)
            for index in range(len(samples) - 1):
                house = observed[index]
                if house is None or observed[index + 1] != house:
                    continue
                start_index = house - 1
                end_index = house % 12
                dt = times[index + 1] - times[index]
                if node_key.startswith("calculated_point:") and sampled_sects[index] != sampled_sects[index + 1]:
                    safety_houses.update({house, 1 if house == 12 else house + 1, 12 if house == 1 else house - 1})
                    continue
                body_speed = max(abs(node_speed(index)), abs(node_speed(index + 1)))
                for cusp_index, adjacent in ((start_index, 12 if house == 1 else house - 1), (end_index, 1 if house == 12 else house + 1)):
                    cusp_speed = max(abs(float(samples[index][2][cusp_index])), abs(float(samples[index + 1][2][cusp_index])))
                    margin = min(
                        abs(((node_lon(index) - float(samples[index][0][cusp_index]) + 180) % 360) - 180),
                        abs(((node_lon(index + 1) - float(samples[index + 1][0][cusp_index]) + 180) % 360) - 180),
                    )
                    if margin <= (body_speed + cusp_speed) * dt * profile.speed_envelope_factor:
                        safety_houses.add(adjacent)
            possible.update(safety_houses)
            classification = "invariant" if len(possible) == 1 and None not in observed else "variable"
            memberships[node_key] = evidence_record(
                feature_key=f"terrestrial_frame:house_membership:{node_key}",
                classification=classification,
                value_kind="natal_house_number",
                possibilities=(str(value) for value in sorted(possible)),
                prerequisite_refs=[f"terrestrial_frame:cusp:{index}" for index in range(1, 13)] + [f"coordinate:{node_key}"],
                transitions=transition_witnesses(observed, times, coordinate_unit="jd_ut"),
                availability="available",
                status_reason=("continuous boundary envelope admits adjacent house" if safety_houses else None),
            )
            if node_key == "angle:Vertex":
                continue
            if node_key.startswith("calculated_point:") and len(set(sampled_sects)) > 1:
                continue
            node_path = _unwrap_path([node_lon(index) for index in range(len(samples))])
            node_speeds = [node_speed(index) for index in range(len(samples))]
            for angle_name, (_, angle_index, multiplier, offset) in angle_sources.items():
                angle_path = _unwrap_path([
                    (float(sample[1][angle_index]) * multiplier + offset) % 360
                    for sample in samples
                ])
                angle_speeds = [float(sample[3][angle_index]) * multiplier for sample in samples]
                relationship = _classify_longitude_relationship(
                    first_key=node_key,
                    first_name=display_name,
                    first_path=node_path,
                    first_speeds=node_speeds,
                    second_key=f"angle:{angle_name}",
                    second_name=angle_name,
                    second_path=angle_path,
                    second_speeds=angle_speeds,
                    times=times,
                    include_minor=config.include_minor,
                    factor=profile.speed_envelope_factor,
                )
                if relationship is not None:
                    angle_relationships.append(relationship)
        for point_name, point_evidence in calculated_points.items():
            if point_evidence.get("availability") != "available":
                continue
            for body_name in first_positions:
                branch_results = []
                for branch in point_evidence["branches"]:
                    start = branch["sample_index_start"]
                    end = branch["sample_index_end"] + 1
                    if end - start < 2:
                        branch_results.append(None)
                        continue
                    point_path = _unwrap_path([
                        part_of_fortune(sampled_sects[index] == "day", float(samples[index][1][0]), float(samples[index][4]["Sun"]["lon"]), float(samples[index][4]["Moon"]["lon"]))
                        if point_name == "Fortune"
                        else lot(float(samples[index][1][0]), float(samples[index][4]["Sun"]["lon"]), float(samples[index][4]["Moon"]["lon"]), sampled_sects[index] == "day")
                        for index in range(start, end)
                    ])
                    formula = point_specs[point_name][branch["sect"]]
                    point_speeds = [
                        float(samples[index][3][0]) + formula[1] * float(samples[index][4]["Moon"]["speed_lon"]) + formula[2] * float(samples[index][4]["Sun"]["speed_lon"])
                        for index in range(start, end)
                    ]
                    branch_results.append(_classify_longitude_relationship(
                        first_key=f"calculated_point:{point_name}",
                        first_name=point_name,
                        first_path=point_path,
                        first_speeds=point_speeds,
                        second_key=f"body:{body_name}",
                        second_name=body_name,
                        second_path=_unwrap_path([float(samples[index][4][body_name]["lon"]) for index in range(start, end)]),
                        second_speeds=[float(samples[index][4][body_name]["speed_lon"]) for index in range(start, end)],
                        times=times[start:end],
                        include_minor=config.include_minor,
                        factor=profile.speed_envelope_factor,
                    ))
                aspects = {row.get("aspect") for row in branch_results if row is not None and row.get("classification") == "invariant"}
                if len(branch_results) == len(point_evidence["branches"]) and all(row is not None for row in branch_results) and len(aspects) == 1:
                    calculated_point_relationships.append({
                        "a": f"calculated_point:{point_name}",
                        "b": f"body:{body_name}",
                        "a_name": point_name,
                        "b_name": body_name,
                        "classification": "invariant",
                        "aspect": next(iter(aspects)),
                        "formula_branch_evidence": [row["evidence"] for row in branch_results],
                    })
    sun_membership = memberships.get("body:Sun") or {}
    sun_houses = {int(value) for value in (sun_membership.get("possibilities") or {}).get("values", [])}
    sect_values = []
    if config.include_sect and sun_houses:
        if sun_houses & {7, 8, 9, 10, 11, 12}:
            sect_values.append("day")
        if sun_houses & {1, 2, 3, 4, 5, 6}:
            sect_values.append("night")
    sect = evidence_record(
        feature_key="terrestrial_frame:sect",
        classification=("invariant" if len(sect_values) == 1 else "variable" if len(sect_values) > 1 else "unavailable"),
        value_kind="day_night_sect",
        possibilities=sect_values,
        prerequisite_refs=["terrestrial_frame:house_membership:body:Sun"],
        availability=("available" if sect_values else "disabled" if not config.include_sect else "prerequisite_unavailable"),
        status_reason=(None if sect_values else "sect disabled by configuration" if not config.include_sect else "Sun house membership unavailable"),
    )
    return {
        "status": "complete",
        "house_system": config.house_system,
        "evaluation_count": len(times),
        "interval": {"start_jd": start_jd, "end_jd": end_jd, "boundary_policy": "inclusive"},
        "coordinates": coordinates,
        "cusp_semantics": cusp_semantics,
        "house_memberships": memberships,
        "angle_relationships": angle_relationships,
        "calculated_points": calculated_points,
        "calculated_point_relationships": calculated_point_relationships,
        "sect": sect,
        "failures": [],
    }

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

def declination_position(
    swe: Any,
    jd_ut: float,
    swe_id: int,
    ephemeris_mode: str = "auto",
    *,
    include_speeds: bool = False,
) -> dict[str, Any] | None:
    flags = ephemeris_flag(swe, ephemeris_mode) | swe.FLG_SPEED | swe.FLG_EQUATORIAL
    pos, err = safe_planet_position(swe, jd_ut, swe_id, flags)
    if err or pos is None:
        return None
    result = {"right_ascension": pos["lon"], "declination": pos["lat"], "declination_pretty": None if pos["lat"] is None else f"{pos['lat']:.5f}°", "ephemeris_actual": pos["ephemeris_actual"], "ephemeris_return_flags": pos["ephemeris_return_flags"]}
    if include_speeds:
        result.update({"right_ascension_speed": pos["speed_lon"], "declination_speed": pos["speed_lat"]})
    return result

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


def evaluate_bounded_natal_interval(
    birth: BoundedBirthData,
    config: ProviderConfig | None = None,
    *,
    profile: IntervalProofProfile | None = None,
) -> dict[str, Any]:
    """Evaluate ordinary configured natal bodies across a normalized birth interval."""
    try:
        import swisseph as swe
    except ImportError as exc:
        raise ImportError("Bounded natal computation requires pyswisseph (`pip install pyswisseph`).") from exc
    config = config or ProviderConfig()
    swe.set_ephe_path(config.ephe_path)
    basis = birth.resolved_birth_time_basis
    if basis is None:
        raise ValueError("bounded birth data must have a normalized birth_time_basis")
    start_dt = datetime.fromisoformat(basis.start_utc)
    end_dt = datetime.fromisoformat(basis.end_utc)
    start_jd, _ = datetime_to_jd_ut(swe, start_dt)
    end_jd, _ = datetime_to_jd_ut(swe, end_dt)
    bodies = base_body_map(swe)
    flags = ephemeris_flag(swe, config.ephemeris_mode) | swe.FLG_SPEED

    def point_positions(jd_ut: float) -> dict[str, dict[str, Any]]:
        positions = {}
        for name, swe_id in bodies.items():
            position, error = safe_planet_position(swe, jd_ut, swe_id, flags)
            if error or position is None:
                raise RuntimeError(f"{name}: {error or 'unknown calculation failure'}")
            equatorial_flags = flags | swe.FLG_EQUATORIAL
            equatorial, equatorial_error = safe_planet_position(swe, jd_ut, swe_id, equatorial_flags)
            if equatorial_error or equatorial is None:
                reason = equatorial_error or "unknown equatorial calculation failure"
                for key in ("right_ascension", "right_ascension_speed", "declination", "declination_speed"):
                    position[f"{key}_availability"] = "provider_failure"
                    position[f"{key}_status_reason"] = reason
            else:
                position.update(
                    {
                        "right_ascension": equatorial["lon"],
                        "declination": equatorial["lat"],
                        "right_ascension_speed": equatorial["speed_lon"],
                        "declination_speed": equatorial["speed_lat"],
                    }
                )
            positions[name] = position
        return positions

    result = evaluate_interval(
        start_jd,
        end_jd,
        bodies,
        point_positions,
        include_minor=config.include_minor,
        include_antiscia=config.include_antiscia,
        include_harmonics=config.include_harmonics,
        harmonic_numbers=config.harmonic_numbers,
        profile=profile,
    )
    result["terrestrial_frame"] = evaluate_terrestrial_frame_interval(
        swe, start_jd, end_jd, birth.birth_lat, birth.birth_lon, config, profile or IntervalProofProfile(), point_positions
    )
    sect = result["terrestrial_frame"]["sect"]
    sect_values = (sect.get("possibilities") or {}).get("values") or []
    triplicity = {}
    for name, body in result["bodies"].items():
        sign_dignity = body.get("sign_dignity") or {}
        sign = sign_dignity.get("sign")
        if len(sect_values) == 1 and sign:
            ruler = dignity_for(name, sign, sect_values[0] == "day")["triplicity_ruler"]
            triplicity[name] = evidence_record(
                feature_key=f"body:{name}:triplicity",
                classification="invariant",
                value_kind="sect_triplicity_ruler",
                possibilities=[ruler],
                prerequisite_refs=[f"body:{name}:sign", "terrestrial_frame:sect"],
                availability="available",
            )
        else:
            triplicity[name] = evidence_record(
                feature_key=f"body:{name}:triplicity",
                classification="variable" if sign and len(sect_values) > 1 else "unavailable",
                value_kind="sect_triplicity_ruler",
                prerequisite_refs=[f"body:{name}:sign", "terrestrial_frame:sect"],
                availability="prerequisite_variable_or_unavailable",
            )
    result["sect_triplicity"] = triplicity
    optional_requests = {
        "Chiron": config.include_optional_points,
        "asteroids": config.include_asteroids,
        "fixed_stars": config.include_fixed_stars,
    }
    result["optional_external_features"] = {
        name: evidence_record(
            feature_key=f"optional_external_feature:{name}",
            classification="unavailable",
            value_kind="optional_external_data_feature",
            prerequisite_refs=[f"qualified_external_data_profile:{name}"],
            availability="unsupported_profile" if requested else "disabled",
            status_reason=(
                "no external-data-backed bounded Natal profile is qualified"
                if requested
                else "feature disabled by configuration"
            ),
        )
        for name, requested in optional_requests.items()
    }
    result["birth_time_basis"] = basis.as_dict()
    result["configured_body_names"] = list(bodies)
    result["ephemeris_mode_requested"] = config.ephemeris_mode
    return result

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
    observed_ephemerides = set()
    requested_flags = ephemeris_flag(swe, config.ephemeris_mode) | swe.FLG_SPEED
    for name, swe_id in active_bodies.items():
        pos, err = safe_planet_position(swe, birth_jd_ut, swe_id, requested_flags)
        if err or pos is None:
            logger.warning("Skipping natal body %s: %s", name, err or "unknown calculation failure")
            skipped_optional.append({"name": name, "swe_id": swe_id, "reason": err or "unknown calculation failure"})
            continue
        observed_ephemerides.add(pos["ephemeris_actual"])
        body = {"name": f"n{name}", "lon": pos["lon"], "lat": pos["lat"], "speed_lon": pos["speed_lon"], "retrograde": pos["retrograde"], "house": house_for_lon(pos["lon"], houses["cusps"]), "pretty": pos["pretty"], "absolute_dms": pos["absolute_dms"], "type": "planet_or_point"}
        if config.include_declinations:
            dec = declination_position(swe, birth_jd_ut, swe_id, config.ephemeris_mode)
            if dec:
                observed_ephemerides.add(dec["ephemeris_actual"])
                body.update(dec)
        natal[f"n{name}"] = body
    for angle_name in ["ASC", "DSC", "MC", "IC"]:
        natal[f"n{angle_name}"] = {"name": f"n{angle_name}", "lon": houses[angle_name], "lat": None, "speed_lon": None, "retrograde": False, "house": "-", "pretty": format_zodiac(houses[angle_name]), "absolute_dms": decimal_to_dms(houses[angle_name]), "type": "angle"}
    validate_ephemeris_mode(config.ephemeris_mode, observed_ephemerides)
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
    return {"type":"natal_chart","person":birth.name,**({"source_chart_id":birth.source_chart_id} if birth.source_chart_id else {}),"birth_local":birth.birth_local,"birth_timezone":birth.birth_timezone,"birth_utc":birth_utc_dt.isoformat(),"birth_lat":birth.birth_lat,"birth_lon":birth.birth_lon,"birth_location_label":birth.birth_location_label,"jd_ut":birth_jd_ut,"house_system":config.house_system,"ephemeris_runtime":{"requested_mode":config.ephemeris_mode,"observed_modes":sorted(observed_ephemerides),"returned_flags_recorded":True},"calculation_options":{"include_declinations":config.include_declinations,"include_dignities":config.include_dignities,"include_sect":config.include_sect,"include_antiscia":config.include_antiscia,"include_harmonics":config.include_harmonics,"harmonic_numbers":list(config.harmonic_numbers),"include_optional_points":config.include_optional_points,"include_asteroids":config.include_asteroids,"include_fixed_stars":config.include_fixed_stars},"calculation_warnings":{"skipped_optional_bodies":skipped_optional,"skipped_fixed_stars":skipped_stars},"sect":{"is_day_chart":day_birth,"sect_light":"Sun" if day_birth else "Moon","out_of_sect_light":"Moon" if day_birth else "Sun"},"houses":{str(i):{"lon":houses["cusps"][i-1],"pretty":format_zodiac(houses["cusps"][i-1]),"traditional_ruler":trad_rulers[i]["ruler"],"modern_ruler":modern_rulers[i]["ruler"]} for i in range(1,13)},"angles":{k:houses[k] for k in ["ASC","DSC","MC","IC"]},"bodies":natal,"lots":lots,"fixed_stars":fixed_star_records,"declination_aspects":declination_aspects(decl_bodies) if config.include_declinations else [],"natal_planet_aspects":all_aspects(natal_planets,natal_planets,"natal","natal",include_minor=config.include_minor),"natal_planet_angle_aspects":all_aspects(natal_planets,natal_angles,"natal","natal",include_minor=config.include_minor),"natal_planet_point_aspects":all_aspects(natal_planets,natal_points,"natal","natal",include_minor=config.include_minor)}
