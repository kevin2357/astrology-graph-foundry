from __future__ import annotations

from astrology_graph_foundry.doctor import (
    build_doctor_report,
    render_doctor_report,
    required_mode_failures,
)
from astrology_graph_foundry.pipelines import eclipse_lunation, solar_return


def test_doctor_report_is_structured_and_renderable():
    report = build_doctor_report()
    assert report["report_type"] == "astrology_graph_foundry_doctor"
    assert report["foundry"]["package_version"] == "0.8.0"
    assert "semantic_projection_core" not in report
    assert "project_saved_packages" not in report["capabilities"]
    assert "live_ephemeris_calculation" in report["capabilities"]
    assert "Astrology Graph Foundry doctor" in render_doctor_report(report)
    assert report["runtime_resources"]["resource_count"] >= 34
    assert len(report["runtime_resources"]["manifest_sha256"]) == 64
    assert report["calculation_contracts"]["profile"] == "agf.calculation_profile.v1.1.0"


def test_doctor_required_mode_failure_codes_are_stable():
    report = build_doctor_report()
    report["foundry"]["version_metadata_matches_runtime"] = True
    report["runtime_resources"]["resource_count"] = 34
    report["swiss_ephemeris"]["available"] = True
    assert required_mode_failures(report, "saved") == []
    assert required_mode_failures(report, "live") == []
    report["swiss_ephemeris"]["available"] = False
    assert required_mode_failures(report, "live") == ["pyswisseph_missing"]


def test_eclipse_classification_is_explicit_about_precision():
    row = eclipse_lunation._eclipse_classification("new_moon", 5.0)
    assert row["eclipse_status"] == "eclipse_season_candidate"
    assert row["potential_eclipse_kind"] == "solar_eclipse"
    assert row["classification_precision"] == "eclipse_season_window_not_global_eclipse_confirmation"

    ordinary = eclipse_lunation._eclipse_classification("full_moon", 30.0)
    assert ordinary["eclipse_status"] == "ordinary_lunation"
    assert ordinary["potential_eclipse_kind"] is None


def test_solar_return_analysis_view_is_compact(monkeypatch):
    package = {
        "metadata": {"analysis_type": "solar_return_dataset", "schema_version": "2.0.0"},
        "target": {"chart_identity": {"chart_id": "natal:test"}},
        "return_location": {"location_label": "Test"},
        "return_event": {"event_utc": "2026-01-01T00:00:00+00:00"},
        "return_chart": {"bodies": {"Sun": {"lon": 10}}, "angles": {}, "houses": {}, "lots": {}, "sect": {}},
        "canonical_astrology_graph": {
            "summary": {"object_count": 1, "relationship_count": 1},
            "objects": [{"id": "obj:Sun", "object_type": "planet_or_point", "name": "Sun"}],
            "relationships": [{"id": "rel:1", "orb": 1.0}],
        },
        "structural_evidence_graph": {},
        "semantic_boundary": {},
        "report_materials": {"recommended_sections": ["Summary"]},
    }
    view = solar_return.analysis_view(package)
    assert view["metadata"]["view_type"] == "solar_return_analysis"
    assert len(view["top_objects"]) == 1
    assert len(view["top_relationships"]) == 1
