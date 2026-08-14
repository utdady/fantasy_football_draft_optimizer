import random

from draftopt.draft.cpu import CPU_POLICIES, choose_cpu_player, cpu_pick
from draftopt.draft.state import create_draft, record_user_pick


def test_cpu_policies_smoke(catalog, conn):
    draft_id = create_draft(conn, user_slot=2)
    # slot 2 → CPU picks first
    for policy in CPU_POLICIES:
        # fresh draft each time
        did = create_draft(conn, user_slot=2)
        state = cpu_pick(conn, did, rng=random.Random(0), policy=policy)
        assert state["picks"]
        assert state["picks"][0]["made_by"] == "cpu"


def test_adp_greedy_is_deterministic(catalog, conn):
    draft_id = create_draft(conn, user_slot=2)
    a = choose_cpu_player(conn, draft_id, rng=random.Random(1), policy="adp_greedy")
    b = choose_cpu_player(conn, draft_id, rng=random.Random(99), policy="adp_greedy")
    assert a == b


def test_choose_rejects_unknown_policy(catalog, conn):
    draft_id = create_draft(conn, user_slot=2)
    try:
        choose_cpu_player(conn, draft_id, policy="nope")
        assert False, "expected ValueError"
    except ValueError:
        pass
