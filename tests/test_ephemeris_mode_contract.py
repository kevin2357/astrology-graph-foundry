from __future__ import annotations

import subprocess
import sys

import pytest

from astrology_graph_foundry.ephemeris.live_natal import (
    ephemeris_flag,
    planet_position,
    validate_ephemeris_mode,
)
from astrology_graph_foundry.ephemeris.models import ProviderConfig


class FakeSwiss:
    FLG_JPLEPH = 1
    FLG_SWIEPH = 2
    FLG_MOSEPH = 4
    FLG_SPEED = 8

    def __init__(self, returned_flags: int):
        self.returned_flags = returned_flags

    def calc_ut(self, jd_ut, swe_id, flags):
        return ([10.0, 1.0, 1.0, -0.25, 0.0, 0.0], self.returned_flags | self.FLG_SPEED)


def test_explicit_moshier_request_records_actual_returned_mode():
    swe = FakeSwiss(FakeSwiss.FLG_MOSEPH)
    result = planet_position(swe, 2451545.0, 0, ephemeris_flag(swe, "moshier") | swe.FLG_SPEED)
    assert result["ephemeris_actual"] == "moshier"
    assert result["ephemeris_return_flags"] == FakeSwiss.FLG_MOSEPH | FakeSwiss.FLG_SPEED


def test_explicit_mode_rejects_silent_fallback_but_auto_allows_observation():
    validate_ephemeris_mode("moshier", {"moshier"})
    validate_ephemeris_mode("auto", {"moshier"})
    with pytest.raises(RuntimeError, match="Requested ephemeris mode 'swiss'"):
        validate_ephemeris_mode("swiss", {"moshier"})


def test_provider_config_rejects_unknown_ephemeris_mode():
    with pytest.raises(ValueError, match="ephemeris_mode"):
        ProviderConfig(ephemeris_mode="unknown")


@pytest.mark.parametrize(
    "command",
    [
        [sys.executable, "-m", "astrology_graph_foundry.cli", "natal", "--help"],
        [sys.executable, "-m", "astrology_graph_foundry.ephemeris.generate_daily_ephemeris", "--help"],
    ],
)
def test_live_cli_surfaces_expose_moshier_and_optional_point_controls(command):
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    assert completed.returncode == 0, completed.stderr
    assert "--ephemeris-mode" in completed.stdout
    assert "--no-optional-points" in completed.stdout
