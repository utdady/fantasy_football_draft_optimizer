"""Unit tests for frozen ADP→value curve (no outcomes)."""

from draftopt.phase2.adp_value_curve import (
    ADP_REF,
    CURVE_ID,
    V_FLOOR,
    V_MAX,
    adp_to_value,
    curve_meta,
)


def test_curve_id_frozen():
    assert CURVE_ID == "adp_linear_v1_2024_ffc12"
    assert curve_meta()["frozen"] is True


def test_adp_to_value_monotone():
    assert adp_to_value(None) is None
    assert adp_to_value(1.0) == V_MAX
    assert adp_to_value(ADP_REF) == V_FLOOR
    assert adp_to_value(ADP_REF + 10) == V_FLOOR
    mid = adp_to_value(90.0)
    assert mid is not None
    assert V_FLOOR < mid < V_MAX
    assert adp_to_value(30.0) > adp_to_value(60.0)
