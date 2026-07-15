def test_imports():
    import astrology_graph_foundry
    from astrology_graph_foundry.pipelines import annual_profections, davison, eclipse_lunation, lunar_return, natal, synastry, composite, transit, solar_return, progressed, solar_arc, timeline, graph
    assert astrology_graph_foundry.__version__
