from draftopt.strategies import get_strategy


def test_p22c_strategy_names():
    assert get_strategy("adp_baseline").name == "adp_baseline"
    assert get_strategy("adp_structural").name == "adp_structural"
    # Must not collide with production defaults
    assert get_strategy("adp").name == "adp"
    assert get_strategy("marginal").name == "marginal"
