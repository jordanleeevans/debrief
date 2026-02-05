from pydantic import BaseModel, Field
from typing import Union, Annotated, Literal
from app.models.enums import Maps, GameModes, Teams

ELIM_MAX = 200
DEATH_MAX = 200
DMG_MAX = 10000
KD_RATIO_MAX = 200.0
ELIM_RATIO_MAX = 200.0
PERCENTAGE_MAX = 100.0

SND_SCORE_MAX = 6
OVERLOAD_SCORE_MAX = 8
HARDPOINT_SCORE_MAX = 250


class WeaponStats(BaseModel):
    """Base model for weapon statistics."""

    eliminations: int = Field(ge=0, le=ELIM_MAX, description="Number of eliminations")
    elimination_death_ratio: float = Field(
        ge=0, le=ELIM_RATIO_MAX, description="Elimination to death ratio"
    )
    damage_dealt: int = Field(ge=0, le=DMG_MAX, description="Total damage dealt")
    headshot_kills: int = Field(
        ge=0, le=ELIM_MAX, description="Number of headshot kills"
    )
    headshot_percentage: float = Field(
        ge=0, le=PERCENTAGE_MAX, description="Percentage of shots that were headshots"
    )
    accuracy_percentage: float = Field(
        ge=0, le=PERCENTAGE_MAX, description="Percentage of shots that hit the target"
    )


class PrimaryWeaponStats(WeaponStats):
    primary_weapon_name: str = Field(..., description="Name of the primary weapon")


class SecondaryWeaponStats(WeaponStats):
    secondary_weapon_name: str = Field(..., description="Name of the secondary weapon")


class MeleeWeaponStats(BaseModel):
    melee_weapon_name: str = Field(..., description="Name of the melee weapon")
    kill_death_ratio: float = Field(
        ge=0,
        le=KD_RATIO_MAX,
        description="Ratio of kills to deaths with this melee weapon",
    )
    damage_dealt: int = Field(
        ge=0, le=DMG_MAX, description="Total damage dealt with this melee weapon"
    )


class Scoreboard(BaseModel):
    player: str = Field(..., description="Player's in-game name")
    eliminations: int = Field(ge=0, le=ELIM_MAX, description="Number of eliminations")
    deaths: int = Field(ge=0, le=DEATH_MAX, description="Number of deaths")
    elimination_death_ratio: float = Field(
        ge=0, le=ELIM_RATIO_MAX, description="Elimination to death ratio"
    )
    score: int = Field(ge=0, description="Player's score")


class HardpointScoreboard(Scoreboard):
    time: int = Field(ge=0, description="Time played in hardpoint in seconds")
    objective_captures: int = Field(ge=0, description="Number of objective captures")
    objective_kills: int = Field(ge=0, description="Number of objective kills")
    captures: int = Field(ge=0, description="Number of captures")
    friendly_score: int = Field(
        ge=0, le=HARDPOINT_SCORE_MAX, description="Friendly score"
    )
    enemy_score: int = Field(ge=0, le=HARDPOINT_SCORE_MAX, description="Enemy score")


class OverloadScoreboard(Scoreboard):
    overloads: int = Field(ge=0, description="Number of overloads achieved")
    overload_devices_carrier_killed: int = Field(
        ge=0, description="Number of overload carriers killed"
    )
    friendly_score: int = Field(
        ge=0, le=OVERLOAD_SCORE_MAX, description="Friendly score"
    )
    enemy_score: int = Field(ge=0, le=OVERLOAD_SCORE_MAX, description="Enemy score")


class SearchAndDestroyScoreboard(Scoreboard):
    plants: int = Field(ge=0, description="Number of bomb plants")
    defuses: int = Field(ge=0, description="Number of bomb defuses")
    objective_kills: int = Field(ge=0, description="Number of objective kills")
    objective_score: int = Field(ge=0, description="Objective score")
    friendly_score: int = Field(ge=0, le=SND_SCORE_MAX, description="Friendly score")
    enemy_score: int = Field(ge=0, le=SND_SCORE_MAX, description="Enemy score")


class GameStats(BaseModel):
    primary_weapon_stats: PrimaryWeaponStats = Field(
        ..., description="Primary weapon statistics as shown in Weapon Stats section"
    )
    secondary_weapon_stats: SecondaryWeaponStats = Field(
        ..., description="Secondary weapon statistics as shown in Weapon Stats section"
    )
    melee_weapon_stats: MeleeWeaponStats = Field(
        ..., description="Melee weapon statistics as shown in Weapon Stats section"
    )
    map: Maps = Field(..., description="Map where the game was played")
    team: Teams = Field(..., description="Team of the player")


# Root-level discriminated union for GameStats
class HardpointGameStats(GameStats):
    game_mode: Literal[GameModes.HARDPOINT] = Field(..., description="Game mode played")
    scoreboard: HardpointScoreboard = Field(
        ..., description="Scoreboard statistics for Hardpoint mode"
    )


class OverloadGameStats(GameStats):
    game_mode: Literal[GameModes.OVERLOAD] = Field(..., description="Game mode played")
    scoreboard: OverloadScoreboard = Field(
        ..., description="Scoreboard statistics for Overload mode"
    )


class SearchAndDestroyGameStats(GameStats):
    game_mode: Literal[GameModes.SEARCH_AND_DESTROY] = Field(
        ..., description="Game mode played"
    )
    scoreboard: SearchAndDestroyScoreboard = Field(
        ..., description="Scoreboard statistics for Search and Destroy mode"
    )


GameStats = Annotated[
    Union[
        HardpointGameStats,
        OverloadGameStats,
        SearchAndDestroyGameStats,
    ],
    Field(discriminator="game_mode"),
]
