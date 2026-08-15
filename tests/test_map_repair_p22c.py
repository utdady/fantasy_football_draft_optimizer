"""P2.2C mapping repair: suffixes, aliases, DST team entities."""

from __future__ import annotations

from draftopt.names import fold_person, person_match_fold, strip_generational_suffix
from draftopt.phase2.map_players import map_ffc_players


def test_strip_generational_suffix():
    assert strip_generational_suffix("Travis Etienne Jr.") == "Travis Etienne"
    assert strip_generational_suffix("James Cook III") == "James Cook"
    assert strip_generational_suffix("Deebo Samuel Sr.") == "Deebo Samuel"
    assert fold_person("Travis Etienne Jr.") == fold_person("Travis Etienne")


def test_hollywood_alias():
    assert person_match_fold("Hollywood Brown") == "marquisebrown"
    assert person_match_fold("Gabe Davis") == "gabrieldavis"
    assert person_match_fold("Michael Badgley") == "mikebadgley"


def test_map_suffix_and_alias_and_dst():
    crosswalk = [
        {
            "player_id": "e1",
            "name": "Travis Etienne",
            "name_fold": fold_person("Travis Etienne"),
            "position": "RB",
            "team": "JAX",
            "sleeper_id": "e1",
            "espn_id": None,
            "fantasypros_id": None,
            "gsis_id": "00-0036973",
        },
        {
            "player_id": "m1",
            "name": "Marquise Brown",
            "name_fold": fold_person("Marquise Brown"),
            "position": "WR",
            "team": "KC",
            "sleeper_id": "m1",
            "espn_id": None,
            "fantasypros_id": None,
            "gsis_id": "00-0035662",
        },
        {
            "player_id": "w1",
            "name": "Kenneth Walker III",
            "name_fold": fold_person("Kenneth Walker III"),
            "position": "RB",
            "team": "SEA",
            "sleeper_id": "w1",
            "espn_id": None,
            "fantasypros_id": None,
            "gsis_id": "00-0038134",
        },
    ]
    ffc = [
        {
            "ffc_player_id": "1",
            "name": "Travis Etienne Jr.",
            "position": "RB",
            "team": "JAX",
            "adp": 17.0,
        },
        {
            "ffc_player_id": "2",
            "name": "Hollywood Brown",
            "position": "WR",
            "team": "KC",
            "adp": 80.0,
        },
        {
            "ffc_player_id": "3",
            "name": "Kenneth Walker",
            "position": "RB",
            "team": "SEA",
            "adp": 35.0,
        },
        {
            "ffc_player_id": "4",
            "name": "Baltimore Defense",
            "position": "DST",
            "team": "BAL",
            "adp": 130.0,
        },
    ]
    report = map_ffc_players(ffc, crosswalk)
    assert report["name_only_joins"] == 0
    assert report["n_mapped"] == 4
    assert report["n_unresolved"] == 0
    by_ffc = {m["source_player_id"]: m for m in report["mapped"]}
    assert by_ffc["1"]["gsis_id"] == "00-0036973"
    assert by_ffc["2"]["method"] == "name_pos_team_alias"
    assert by_ffc["3"]["player_id"] == "w1"
    assert by_ffc["4"]["player_id"] == "dst:BAL"
    assert by_ffc["4"]["method"] == "dst_team"
    assert by_ffc["4"]["gsis_id"] is None
