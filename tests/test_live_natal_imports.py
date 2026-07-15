def test_live_natal_imports():
    from astro_analysis_sdk.ephemeris.live_natal import build_live_natal_chart
    from astro_analysis_sdk.ephemeris.models import BirthData
    assert build_live_natal_chart
    assert BirthData
