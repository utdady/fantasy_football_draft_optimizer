from draftopt.strategies import get_strategy


def test_p22c_strategy_names():
    assert get_strategy("adp_baseline").name == "adp_baseline"
    assert get_strategy("adp_structural").name == "adp_structural"
    assert get_strategy("adp_v3a").name == "adp_v3a"
    assert get_strategy("adp_v3b").name == "adp_v3b"
    # Must not collide with production defaults
    assert get_strategy("adp").name == "adp"
    assert get_strategy("marginal").name == "marginal"
