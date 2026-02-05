import pytest

# Skip these tests when Pydantic isn't available in the environment
pytest.importorskip("pydantic")
from pydantic import ValidationError

from app.models import schemas
from app.models.enums import GameModes, Maps, Teams
from app.models.schemas import (HardpointGameStats, HardpointScoreboard,
                                SearchAndDestroyScoreboard, WeaponStats)


def test_weaponstats_valid_and_invalid():
    valid = WeaponStats(
        eliminations=10,
        elimination_death_ratio=1.0,
        damage_dealt=100,
        headshot_kills=2,
        headshot_percentage=10.0,
        accuracy_percentage=20.0,
    )
    assert valid.eliminations == 10

    with pytest.raises(ValidationError):
        WeaponStats(
            eliminations=schemas.ELIM_MAX + 1,
            elimination_death_ratio=1.0,
            damage_dealt=100,
            headshot_kills=0,
            headshot_percentage=10.0,
            accuracy_percentage=20.0,
        )


def test_hardpoint_scoreboard_limits():
    valid = HardpointScoreboard(
        player="player1",
        eliminations=1,
        deaths=0,
        elimination_death_ratio=1.0,
        score=10,
        time=100,
        objective_captures=0,
        objective_kills=0,
        captures=0,
        friendly_score=schemas.HARDPOINT_SCORE_MAX,
        enemy_score=0,
    )
    assert valid.friendly_score == schemas.HARDPOINT_SCORE_MAX

    with pytest.raises(ValidationError):
        HardpointScoreboard(
            player="player1",
            eliminations=1,
            deaths=0,
            elimination_death_ratio=1.0,
            score=10,
            time=100,
            objective_captures=0,
            objective_kills=0,
            captures=0,
            friendly_score=schemas.HARDPOINT_SCORE_MAX + 1,
            enemy_score=0,
        )


def test_discriminated_union_rejects_wrong_scoreboard():
    # Build a SearchAndDestroy scoreboard payload
    sd_payload = {
        "player": "p",
        "eliminations": 1,
        "deaths": 0,
        "elimination_death_ratio": 1.0,
        "score": 5,
        "plants": 0,
        "defuses": 0,
        "objective_kills": 0,
        "objective_score": 0,
        "friendly_score": 0,
        "enemy_score": 0,
    }

    # Using a Hardpoint game_mode with a SearchAndDestroy scoreboard should fail validation
    payload = {
        "primary_weapon_stats": {
            "eliminations": 0,
            "elimination_death_ratio": 0.0,
            "damage_dealt": 0,
            "headshot_kills": 0,
            "headshot_percentage": 0.0,
            "accuracy_percentage": 0.0,
        },
        "secondary_weapon_stats": {
            "eliminations": 0,
            "elimination_death_ratio": 0.0,
            "damage_dealt": 0,
            "headshot_kills": 0,
            "headshot_percentage": 0.0,
            "accuracy_percentage": 0.0,
        },
        "melee_weapon_stats": {
            "melee_weapon_name": "knife",
            "kill_death_ratio": 0.0,
            "damage_dealt": 0,
        },
        "map": Maps.SCAR,
        "team": Teams.JSOC,
        "game_mode": GameModes.HARDPOINT,
        "scoreboard": sd_payload,
    }

    with pytest.raises(ValidationError):
        HardpointGameStats(**payload)
