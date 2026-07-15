from __future__ import annotations

import pytest

from astrology_graph_foundry.projection_adapter import (
    TemporalProjectionNotImplementedError,
    project_dataset,
    reject_unsupported_temporal_projection,
)


def static_package() -> dict:
    return {
        "metadata": {
            "analysis_type": "natal_dataset",
            "source_chart_id": "natal:test",
            "source_chart_ids": ["natal:test"],
            "sensor_instance_id": "natal:test",
        },
        "canonical_astrology_graph": {
            "graph_type": "canonical_astrology_graph",
            "graph_version": "1.3.0",
            "objects": [],
            "relationships": [],
        },
        "structural_evidence_graph": {"graph_version": "1.3.0"},
    }


@pytest.mark.parametrize(
    "analysis_type",
    ["transit_dataset", "transit_range_dataset", "transit_period_dataset"],
)
def test_temporal_activation_packages_fail_explicitly(analysis_type: str):
    package = static_package()
    package["metadata"]["analysis_type"] = analysis_type
    with pytest.raises(
        TemporalProjectionNotImplementedError,
        match="projected_temporal_activation_graph.v1",
    ):
        project_dataset(package)


def test_static_package_is_not_rejected_by_temporal_guard():
    reject_unsupported_temporal_projection(static_package())


def test_solar_return_is_not_blanket_rejected_as_temporal_activation():
    package = static_package()
    package["metadata"]["analysis_type"] = "solar_return_dataset"
    reject_unsupported_temporal_projection(package)
