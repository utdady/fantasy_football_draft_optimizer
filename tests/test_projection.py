from draftopt.projection import resolve_projection
from draftopt.strategies.marginal import MarginalValueStrategy
from draftopt.draft.state import create_draft


def test_resolve_espn_from_proj_espn():
    p = resolve_projection({"proj_espn": 250.5, "ecr_fp_ppr": 10})
    assert p.value == 250.5
    assert p.source == "espn"
    assert p.quality == "high"


def test_resolve_espn_from_season_points():
    p = resolve_projection({"season_points": 180.0})
    assert p.source == "espn"
    assert p.quality == "high"


def test_resolve_ecr_proxy_is_low_quality():
    p = resolve_projection({"ecr_fp_ppr": 50})
    assert p.value == 300.0
    assert p.source == "ecr_proxy"
    assert p.quality == "low"


def test_resolve_none():
    p = resolve_projection({})
    assert p.value == 0.0
    assert p.source == "none"
    assert p.quality == "none"


def test_marginal_recommend_exposes_lineage(catalog, conn):
    draft_id = create_draft(conn, user_slot=1)
    recs = MarginalValueStrategy().recommend(conn, draft_id, n=1)
    assert recs
    assert recs[0]["projection_source"] == "espn"
    assert recs[0]["projection_quality"] == "high"
