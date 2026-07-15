from __future__ import annotations

from typing import Any

VALID_RETURN_LOCATION_POLICIES = ("target_reference", "explicit")


def resolve_return_location(
    *,
    target: Any,
    return_location_policy: str,
    location_timezone: str | None = None,
    location_lat: float | None = None,
    location_lon: float | None = None,
    location_label: str | None = None,
) -> dict[str, Any]:
    """Resolve the location used to cast Solar/Lunar Return houses and angles.

    The policy is intentionally mandatory.  A caller must explicitly choose
    either the TransitableChart reference location or an explicit lived/event
    location; the Foundry does not silently choose between those interpretive
    policies.
    """
    if return_location_policy not in VALID_RETURN_LOCATION_POLICIES:
        valid = ", ".join(VALID_RETURN_LOCATION_POLICIES)
        raise ValueError(
            "--return-location-policy is mandatory and must be one of "
            f"{valid}. For simple testing, or when the TransitableChart "
            "reference event is truly the desired return location, use "
            "--return-location-policy target_reference."
        )

    ref = target.reference_event or {}

    if return_location_policy == "target_reference":
        if any(value is not None for value in (
            location_timezone, location_lat, location_lon, location_label
        )):
            raise ValueError(
                "Location override fields cannot be combined with "
                "--return-location-policy target_reference. Use "
                "--return-location-policy explicit when supplying a return location."
            )
        timezone = ref.get("timezone") or "UTC"
        lat = ref.get("lat")
        lon = ref.get("lon")
        label = ref.get("location_label") or "TransitableChart reference location"
        if lat is None or lon is None:
            raise ValueError(
                "The target_reference policy requires latitude and longitude in "
                "TransitableChart.reference_event. Supply an explicit location with "
                "--return-location-policy explicit instead."
            )
        return {
            "policy": "target_reference",
            "timezone": str(timezone),
            "lat": float(lat),
            "lon": float(lon),
            "location_label": str(label),
            "source": "transitable_chart.reference_event",
        }

    missing = [
        name for name, value in (
            ("--location-timezone", location_timezone),
            ("--location-lat", location_lat),
            ("--location-lon", location_lon),
            ("--location-label", location_label),
        )
        if value is None
    ]
    if missing:
        raise ValueError(
            "--return-location-policy explicit requires all explicit location "
            f"fields: {', '.join(missing)}."
        )
    return {
        "policy": "explicit",
        "timezone": str(location_timezone),
        "lat": float(location_lat),
        "lon": float(location_lon),
        "location_label": str(location_label),
        "source": "cli_or_api_explicit_location",
    }
