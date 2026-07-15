def test_imports():
    import astro_analysis_sdk
    from astro_analysis_sdk.pipelines import annual_profections, davison, eclipse_lunation, lunar_return, natal, synastry, composite, transit, solar_return, progressed, solar_arc, timeline, graph
    assert astro_analysis_sdk.__version__
