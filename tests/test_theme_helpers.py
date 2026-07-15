from astrology_graph_foundry.common.themes import theme_tags, operator_hints

def test_theme_tags():
    assert 'communication' in theme_tags('Mercury')

def test_operator_hints():
    assert any(h['operator']=='translate' for h in operator_hints('Mercury'))
