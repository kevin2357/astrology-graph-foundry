from astro_analysis_sdk.common.chart_graph import (
    REL_ASPECT,
    REL_TRANSIT_ACTIVATION,
    canonical_relationship_type,
)


def test_legacy_relationship_type_aliases():
    assert canonical_relationship_type("aspect") == REL_ASPECT
    assert canonical_relationship_type("transit_to_natal_object_aspect") == REL_TRANSIT_ACTIVATION
    assert canonical_relationship_type("contra-parallel") == "DECLINATION_CONTRAPARALLEL"
