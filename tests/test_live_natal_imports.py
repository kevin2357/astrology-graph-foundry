def test_live_natal_imports():
    from astrology_graph_foundry.ephemeris.live_natal import build_live_natal_chart
    from astrology_graph_foundry.ephemeris.models import BirthData
    assert build_live_natal_chart
    assert BirthData
