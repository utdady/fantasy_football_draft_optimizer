from draftopt.draft.state import round_for_pick, team_for_pick


def test_odd_round_goes_1_to_10():
    assert [team_for_pick(n, n_teams=10) for n in range(1, 11)] == list(range(1, 11))


def test_even_round_reverses():
    assert [team_for_pick(n, n_teams=10) for n in range(11, 21)] == list(range(10, 0, -1))


def test_round_3_starts_at_team_1():
    assert team_for_pick(21, n_teams=10) == 1
    assert round_for_pick(21, n_teams=10) == 3
    assert round_for_pick(10, n_teams=10) == 1
    assert round_for_pick(11, n_teams=10) == 2
