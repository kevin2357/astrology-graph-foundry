from astrology_graph_foundry.pipelines.solar_return import _compact_relationship_selection


def _row(idx, family, owners, orb):
    return {
        "id": f"r{idx}",
        "orb": orb,
        "structural_strength_score": 0.5,
        "evidence_metadata": {
            "evidence_tier": "antiscia" if family == "antiscia_relationship" else "core",
            "derivation_family": family,
            "owner_object_refs": owners,
        },
    }


def test_compact_relationship_selection_diversifies_and_deprioritizes_owner_rows():
    rows = [_row(i, "antiscia_relationship", ["natal:Sun"], 0.0) for i in range(20)]
    rows += [_row(100 + i, "direct_aspect", [f"a{i}", f"b{i}"], 0.5 + i / 10) for i in range(8)]
    selected = _compact_relationship_selection(rows, limit=10)
    assert len(selected) == 10
    assert sum((r["evidence_metadata"]["derivation_family"] == "antiscia_relationship") for r in selected) <= 4
    assert selected[0]["evidence_metadata"]["derivation_family"] == "direct_aspect"
