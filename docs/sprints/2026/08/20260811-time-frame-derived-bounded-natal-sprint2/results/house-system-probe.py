"""Emit the controlled Swiss Ephemeris house-system audit matrix as JSON."""

from __future__ import annotations

import json

import swisseph as swe


JULIAN_DAY = swe.julday(2020, 1, 1, 12)
LONGITUDE = -104.9903
HOUSE_SYSTEMS = "PKORCAEVXHTBMUWZ"
LATITUDES = (0.0, 39.7392, 66.0, 66.6, 67.0, 80.0, 89.9)


rows = []
for code in HOUSE_SYSTEMS:
    for latitude in LATITUDES:
        row = {
            "code": code,
            "name": swe.house_name(code.encode("ascii")),
            "latitude": latitude,
        }
        try:
            cusps, ascmc = swe.houses_ex(
                JULIAN_DAY,
                latitude,
                LONGITUDE,
                code.encode("ascii"),
            )
        except Exception as exc:  # provider behavior is the evidence under test
            row.update(ok=False, error=f"{type(exc).__name__}: {exc}")
        else:
            cusp_1_asc_delta = abs(((cusps[0] - ascmc[0] + 180) % 360) - 180)
            row.update(
                ok=True,
                cusp_count=len(cusps),
                cusp_1=round(cusps[0], 9),
                ascendant=round(ascmc[0], 9),
                midheaven=round(ascmc[1], 9),
                cusp_1_ascendant_delta=round(cusp_1_asc_delta, 9),
            )
        rows.append(row)

print(
    json.dumps(
        {
            "artifact_type": "agf_house_system_provider_probe",
            "swisseph_version": swe.version,
            "julian_day_ut": JULIAN_DAY,
            "longitude": LONGITUDE,
            "house_systems": HOUSE_SYSTEMS,
            "latitudes": LATITUDES,
            "rows": rows,
        },
        indent=2,
    )
)
