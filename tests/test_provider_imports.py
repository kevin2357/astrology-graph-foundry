def test_provider_imports():
    from astrology_graph_foundry.ephemeris.providers import CachedJsonlEphemerisProvider, LiveSwissEphemerisProvider, create_provider
    assert CachedJsonlEphemerisProvider and LiveSwissEphemerisProvider and create_provider
