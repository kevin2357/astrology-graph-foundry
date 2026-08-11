from __future__ import annotations

import pytest

from astrology_graph_foundry.ephemeris.interval_evaluation import IntervalProofProfile
from astrology_graph_foundry.ephemeris.live_natal import (
    evaluate_terrestrial_frame_interval,
    house_data,
)
from astrology_graph_foundry.ephemeris.models import ProviderConfig


class FakeSwe:
    def houses_ex(self, jd, lat, lon, code):
        return tuple(range(240, 600, 30)), (265.0, 175.0, 0.0, 90.0)

    def houses_ex2(self, jd, lat, lon, code):
        offset = (jd - 1.0) * 360.0
        cusps = tuple((350.0 + 30.0 * index + offset) % 360 for index in range(12))
        ascmc = ((350.0 + offset) % 360, (260.0 + offset) % 360, 0.0, (80.0 + offset) % 360)
        return cusps, ascmc, (360.0,) * 12, (360.0, 360.0, 0.0, 360.0)


def test_house_data_preserves_provider_numbering_when_ascendant_differs():
    result = house_data(FakeSwe(), 1.0, 0.0, 0.0, "W")
    assert result["cusps"][0] == 240.0
    assert result["ASC"] == 265.0


def test_provider_config_rejects_unrecognized_or_structurally_incompatible_house_system():
    with pytest.raises(ValueError, match="supported uppercase twelve-house code"):
        ProviderConfig(house_system="Z")
    with pytest.raises(ValueError, match="supported uppercase twelve-house code"):
        ProviderConfig(house_system="G")
    with pytest.raises(ValueError, match="supported uppercase twelve-house code"):
        ProviderConfig(house_system="p")


def test_terrestrial_frame_retains_circular_ranges_and_transition_witnesses():
    result = evaluate_terrestrial_frame_interval(
        FakeSwe(),
        1.0,
        1.0 + 1.0 / 24.0,
        39.0,
        -105.0,
        ProviderConfig(house_system="P"),
        IntervalProofProfile(minimum_step_seconds=3600),
    )
    assert result["status"] == "complete"
    cusp = result["coordinates"]["cusp:1"]
    assert cusp["range_evidence"]["wraps_origin"] is True
    assert cusp["transition_witnesses"]
    assert "angle:Vertex" in result["coordinates"]


def test_unqualified_exact_house_system_is_explicitly_unsupported_in_bounded_mode():
    result = evaluate_terrestrial_frame_interval(
        FakeSwe(),
        1.0,
        1.1,
        0.0,
        0.0,
        ProviderConfig(house_system="R"),
        IntervalProofProfile(),
    )
    assert result["status"] == "unsupported"
    assert result["failures"][0]["reason"] == "house_system_not_qualified_for_bounded_natal"


def test_house_assignment_half_open_wrap_contract():
    from astrology_graph_foundry.common.geometry import house_for_lon

    cusps = [350, 20, 50, 80, 110, 140, 170, 200, 230, 260, 290, 320]
    assert house_for_lon(355, cusps) == 1
    assert house_for_lon(10, cusps) == 1
    assert house_for_lon(20, cusps) == 2
    assert house_for_lon(349, cusps) == 12
