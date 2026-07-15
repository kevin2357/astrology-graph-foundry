from astrology_graph_foundry.pipelines import transit_period

def test_transit_period_module_exports_build():
    assert callable(transit_period.build)
