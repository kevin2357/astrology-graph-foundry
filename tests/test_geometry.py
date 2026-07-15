from astrology_graph_foundry.common.geometry import angular_distance, midpoint, deg_to_sign

def test_angular_distance_wrap(): assert angular_distance(350,10)==20
def test_midpoint_wrap(): assert midpoint(350,10)==0
def test_sign(): assert deg_to_sign(31)['sign']=='Taurus'
