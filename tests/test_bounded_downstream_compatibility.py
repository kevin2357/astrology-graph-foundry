from __future__ import annotations

import json

import pytest

from astrology_graph_foundry.common.package_compatibility import BoundedNatalCompatibilityError
from astrology_graph_foundry.common.transitable_chart import from_package
from astrology_graph_foundry.pipelines import composite, davison


def _bounded_package():
    return {
        "metadata": {"analysis_type": "bounded_natal_dataset", "source_chart_id": "natal:bounded"},
        "canonical_astrology_graph": {
            "graph_type": "bounded_canonical_astrology_graph",
            "graph_version": "1.0.0",
            "objects": [],
            "relationships": [],
        },
    }


def test_transitable_consumers_reject_bounded_family():
    with pytest.raises(BoundedNatalCompatibilityError, match="TransitableChart"):
        from_package(_bounded_package())


def test_synastry_composite_and_davison_reject_bounded_family():
    exact_placeholder = {"metadata": {"analysis_type": "natal_dataset"}, "natal": {}}
    with pytest.raises(BoundedNatalCompatibilityError, match="Composite/Synastry"):
        composite.resolve_pair_inputs(person_a_dataset=_bounded_package(), person_b_dataset=exact_placeholder)
    with pytest.raises(BoundedNatalCompatibilityError, match="Davison"):
        davison.build(person_a_natal_dataset=_bounded_package(), person_b_natal_dataset=exact_placeholder)


def test_saved_and_reloaded_bounded_package_rejects_identically(tmp_path):
    path = tmp_path / "bounded.json"
    path.write_text(json.dumps(_bounded_package()), encoding="utf-8")
    with pytest.raises(BoundedNatalCompatibilityError, match="Composite/Synastry"):
        composite.resolve_pair_inputs(person_a_dataset=str(path), person_b_dataset=str(path))


def test_graph_type_detection_prevents_metadata_bypass():
    package = _bounded_package()
    package["metadata"]["analysis_type"] = "natal_dataset"
    with pytest.raises(BoundedNatalCompatibilityError, match="TransitableChart"):
        from_package(package)
