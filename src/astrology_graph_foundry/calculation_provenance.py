"""Versioned calculation configuration and normalized-input provenance."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict
from datetime import datetime
from decimal import Decimal
from typing import Any
from zoneinfo import ZoneInfo

from astrology_graph_foundry.common.constants import (
    ANGLES,
    ASPECTS,
    DEFAULT_ORBS,
    LUMINARIES,
    MAJOR_ASPECTS,
    OUTER_PLANETS,
    POINTS,
)
from astrology_graph_foundry.ephemeris.models import BirthData, BoundedBirthData, ProviderConfig
from astrology_graph_foundry.ephemeris.uncertainty_evidence import EVIDENCE_CONTRACT_VERSION

CALCULATION_PROVENANCE_CONTRACT_VERSION = "agf.calculation_provenance.v1.0.0"
CALCULATION_PROFILE_VERSION = "agf.calculation_profile.v1.1.0"
BOUNDED_CALCULATION_PROFILE_VERSION = "agf.bounded_natal.calculation_profile.v1.1.0"
NORMALIZATION_POLICY_VERSION = "agf.normalization_policy.v1.0.0"
BOUNDED_NORMALIZATION_POLICY_VERSION = "agf.bounded_birth_time.normalization_policy.v1.0.0"
CANONICAL_JSON_POLICY_VERSION = "agf.canonical_json.v1.0.0"

CORE_BODY_NAMES = (
    "Sun",
    "Moon",
    "Mercury",
    "Venus",
    "Mars",
    "Jupiter",
    "Saturn",
    "Uranus",
    "Neptune",
    "Pluto",
    "True Node",
    "Mean Node",
)


def canonical_json_bytes(value: Any) -> bytes:
    """Serialize a JSON value for hashing under the v1 canonical policy."""

    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def normalize_bounded_source_input(birth_data: BoundedBirthData) -> dict[str, Any]:
    """Normalize bounded geometry inputs without changing the exact-input contract."""

    basis = birth_data.resolved_birth_time_basis
    if basis is None:  # pragma: no cover - dataclass construction guarantees this
        raise ValueError("BoundedBirthData has no normalized birth-time basis")
    return {
        "birth_time_basis": basis.as_dict(),
        "birth_timezone": ZoneInfo(birth_data.birth_timezone).key,
        "birth_lat": _canonical_decimal(birth_data.birth_lat),
        "birth_lon": _canonical_decimal(birth_data.birth_lon),
    }


def build_bounded_source_input_provenance(birth_data: BoundedBirthData) -> dict[str, Any]:
    normalized = normalize_bounded_source_input(birth_data)
    return {
        "normalization_policy_version": BOUNDED_NORMALIZATION_POLICY_VERSION,
        "completeness": "complete_bounded_live_input",
        "sha256": sha256_json(
            {
                "normalization_policy_version": BOUNDED_NORMALIZATION_POLICY_VERSION,
                "values": normalized,
            }
        ),
        "values": normalized,
        "included_fields": ["birth_time_basis", "birth_timezone", "birth_lat", "birth_lon"],
        "excluded_descriptive_fields": ["name", "birth_location_label", "source_chart_id"],
    }


def build_bounded_calculation_provenance(
    *,
    birth_data: BoundedBirthData,
    config: ProviderConfig,
    interval_assessment: dict[str, Any],
) -> dict[str, Any]:
    source_input = build_bounded_source_input_provenance(birth_data)
    profile = {
        "profile_version": BOUNDED_CALCULATION_PROFILE_VERSION,
        "canonical_json_policy_version": CANONICAL_JSON_POLICY_VERSION,
        "normalization_policy_version": BOUNDED_NORMALIZATION_POLICY_VERSION,
        "evidence_contract_version": EVIDENCE_CONTRACT_VERSION,
        "proof_profile": interval_assessment["proof_profile"],
        "ephemeris_mode": config.ephemeris_mode,
        "zodiac": {"framework": "tropical", "ayanamsha": None},
        "object_inclusion": {"core": list(CORE_BODY_NAMES), "optional_file_dependent": False},
        "aspects": {
            "angles_degrees": dict(sorted(ASPECTS.items())),
            "base_orbs_degrees": dict(sorted(DEFAULT_ORBS.items())),
            "include_minor": config.include_minor,
        },
        "bounded_feature_policy": {
            "houses_angles_sect_lots": "unavailable",
            "declinations_antiscia_harmonics_fixed_stars": "deferred",
            "canonical_promotion": "invariant_categories_only",
        },
    }
    return {
        "contract_version": "agf.bounded_natal.calculation_provenance.v1.0.0",
        "calculation_basis_status": "complete_bounded_live_profile",
        "calculation_profile_version": BOUNDED_CALCULATION_PROFILE_VERSION,
        "normalization_policy_version": BOUNDED_NORMALIZATION_POLICY_VERSION,
        "canonical_json_policy_version": CANONICAL_JSON_POLICY_VERSION,
        "source_input": source_input,
        "configuration_sha256": sha256_json(profile),
        "calculation_profile": profile,
        "output_artifact_hash": {
            "owner": "orchestration",
            "status": "not_emitted_by_agf",
            "algorithm": "sha256",
            "boundary": "exact persisted UTF-8 artifact bytes returned by AGF before downstream transformation",
            "reason": "AGF packages contain operational created_at metadata; persistence owns the final byte envelope.",
        },
    }


def _canonical_decimal(value: float) -> str:
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValueError("Calculation coordinates must be finite")
    if numeric == 0:
        return "0"
    return format(Decimal(str(value)).normalize(), "f")


def normalize_source_input(
    birth_data: BirthData | None,
    natal_chart: dict[str, Any] | None = None,
) -> tuple[dict[str, Any] | None, str]:
    """Normalize only facts that determine natal geometry."""

    if birth_data is not None:
        local = datetime.fromisoformat(birth_data.birth_local)
        timezone = ZoneInfo(birth_data.birth_timezone).key
        return (
            {
                "birth_local": local.isoformat(),
                "birth_timezone": timezone,
                "birth_lat": _canonical_decimal(birth_data.birth_lat),
                "birth_lon": _canonical_decimal(birth_data.birth_lon),
            },
            "complete_live_input",
        )

    chart = natal_chart or {}
    required = ("birth_local", "birth_timezone", "birth_lat", "birth_lon")
    if not all(chart.get(name) is not None for name in required):
        return None, "legacy_source_unavailable"
    local = datetime.fromisoformat(str(chart["birth_local"]))
    timezone = ZoneInfo(str(chart["birth_timezone"])).key
    return (
        {
            "birth_local": local.isoformat(),
            "birth_timezone": timezone,
            "birth_lat": _canonical_decimal(chart["birth_lat"]),
            "birth_lon": _canonical_decimal(chart["birth_lon"]),
        },
        "recovered_from_cached_chart",
    )


def build_calculation_profile(
    config: ProviderConfig,
    *,
    provider_runtime: dict[str, Any],
) -> dict[str, Any]:
    config_values = asdict(config)
    config_values.pop("ephe_path", None)
    config_values["harmonic_numbers"] = list(config.harmonic_numbers)
    config_values["asteroid_ids"] = list(config.asteroid_ids)
    config_values["fixed_star_names"] = list(config.fixed_star_names)
    return {
        "profile_version": CALCULATION_PROFILE_VERSION,
        "canonical_json_policy_version": CANONICAL_JSON_POLICY_VERSION,
        "zodiac": {"framework": "tropical", "ayanamsha": None},
        "houses": {"system": config.house_system, "angle_algorithm": "swisseph.houses_ex"},
        "objects": {
            "core": list(CORE_BODY_NAMES),
            "nodes": ["True Node", "Mean Node"],
            "angles": ["ASC", "DSC", "MC", "IC", "Vertex"],
            "optional_chiron": config.include_optional_points,
            "asteroids_enabled": config.include_asteroids,
            "asteroid_ids": list(config.asteroid_ids),
            "fixed_stars_enabled": config.include_fixed_stars,
            "fixed_star_names": list(config.fixed_star_names),
        },
        "aspects": {
            "angles_degrees": dict(sorted(ASPECTS.items())),
            "base_orbs_degrees": dict(sorted(DEFAULT_ORBS.items())),
            "major": sorted(MAJOR_ASPECTS),
            "included": sorted(ASPECTS if config.include_minor else MAJOR_ASPECTS),
            "body_adjustments_degrees": {
                "luminary": {"members": sorted(LUMINARIES), "delta": 1.0},
                "angle": {"members": sorted(ANGLES), "delta": 0.5},
                "outer_planet_pair": {"members": sorted(OUTER_PLANETS), "delta": -1.0},
                "point": {"members": sorted(POINTS), "delta": -1.0},
                "minimum_orb": 1.0,
            },
            "declination_parallel_orb_degrees": 1.0,
        },
        "derived": {
            "sect_policy": "sun_house_7_through_12_is_day",
            "fortune_day": "ASC + Moon - Sun",
            "fortune_night": "ASC + Sun - Moon",
            "spirit_day": "ASC + Sun - Moon",
            "spirit_night": "ASC + Moon - Sun",
            "dignities": "lightweight_domicile_exaltation_triplicity_v1",
            "antiscia": "solstitial_axis_v1",
        },
        "normalization": {
            "policy_version": NORMALIZATION_POLICY_VERSION,
            "local_datetime_parser": "python.datetime.fromisoformat",
            "timezone_provider": "python.zoneinfo",
            "utc_conversion": "aware_datetime.astimezone.UTC",
            "coordinate_encoding_for_hash": "normalized_base10_string",
        },
        "provider": provider_runtime,
        "invocation_options": config_values,
    }


def build_calculation_provenance(
    *,
    birth_data: BirthData | None,
    natal_chart: dict[str, Any],
    config: ProviderConfig,
    provider_runtime: dict[str, Any],
) -> dict[str, Any]:
    normalized_input, completeness = normalize_source_input(birth_data, natal_chart)
    profile = build_calculation_profile(config, provider_runtime=provider_runtime)
    return {
        "contract_version": CALCULATION_PROVENANCE_CONTRACT_VERSION,
        "calculation_basis_status": (
            "complete_live_profile"
            if birth_data is not None and provider_runtime.get("mode") == "live_calculation"
            else "cached_replay_profile_not_original_calculation"
        ),
        "calculation_profile_version": CALCULATION_PROFILE_VERSION,
        "normalization_policy_version": NORMALIZATION_POLICY_VERSION,
        "canonical_json_policy_version": CANONICAL_JSON_POLICY_VERSION,
        "source_input": {
            "completeness": completeness,
            "sha256": (
                sha256_json(
                    {
                        "normalization_policy_version": NORMALIZATION_POLICY_VERSION,
                        "values": normalized_input,
                    }
                )
                if normalized_input is not None
                else None
            ),
            "included_fields": ["birth_local", "birth_timezone", "birth_lat", "birth_lon"],
            "excluded_descriptive_fields": ["name", "birth_location_label", "source_chart_id"],
        },
        "configuration_sha256": sha256_json(profile),
        "calculation_profile": profile,
        "output_artifact_hash": {
            "owner": "orchestration",
            "status": "not_emitted_by_agf",
            "algorithm": "sha256",
            "boundary": "exact persisted UTF-8 artifact bytes returned by AGF before downstream transformation",
            "reason": "AGF packages contain operational created_at metadata; the persistence owner hashes the final byte envelope.",
        },
    }
