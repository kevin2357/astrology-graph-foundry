def test_provider_imports():
    from astro_analysis_sdk.ephemeris.providers import CachedJsonlEphemerisProvider, LiveSwissEphemerisProvider, create_provider
    assert CachedJsonlEphemerisProvider and LiveSwissEphemerisProvider and create_provider
