from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Annotated, Literal
from app.models.types import PrimaryWeaponType, SecondaryWeaponType, Knife
from app.models.enums import (
    Maps,
    GameModes,
    Teams,
)

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
    primary_weapon_name: PrimaryWeaponType = Field(
        ..., description="Name of the primary weapon"
    )


class SecondaryWeaponStats(WeaponStats):
    secondary_weapon_name: SecondaryWeaponType = Field(
        ..., description="Name of the secondary weapon"
    )


class MeleeWeaponStats(BaseModel):
    melee_weapon_name: Knife = Field(..., description="Name of the melee weapon")
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


class GameStatsResponse(BaseModel):
    """Response model that accepts any game mode variant for API responses."""

    primary_weapon_stats: Optional[PrimaryWeaponStats] = Field(
        None, description="Primary weapon statistics as shown in Weapon Stats section"
    )
    secondary_weapon_stats: Optional[SecondaryWeaponStats] = Field(
        None, description="Secondary weapon statistics as shown in Weapon Stats section"
    )
    melee_weapon_stats: Optional[MeleeWeaponStats] = Field(
        None, description="Melee weapon statistics as shown in Weapon Stats section"
    )
    map: Maps = Field(..., description="Map where the game was played")
    team: Teams = Field(..., description="Team of the player")
    game_mode: GameModes = Field(..., description="Game mode played")
    scoreboard: Union[
        HardpointScoreboard, OverloadScoreboard, SearchAndDestroyScoreboard
    ] = Field(..., description="Scoreboard statistics for the game mode")

    # ensure that the scoreboard type matches the game mode
    @model_validator(mode="after")
    def validate_scoreboard(self):
        game_mode = self.game_mode
        scoreboard = self.scoreboard

        if game_mode == GameModes.HARDPOINT and not isinstance(
            scoreboard, HardpointScoreboard
        ):
            raise ValueError(
                "Scoreboard must be of type HardpointScoreboard for Hardpoint mode"
            )
        elif game_mode == GameModes.OVERLOAD and not isinstance(
            scoreboard, OverloadScoreboard
        ):
            raise ValueError(
                "Scoreboard must be of type OverloadScoreboard for Overload mode"
            )
        elif game_mode == GameModes.SEARCH_AND_DESTROY and not isinstance(
            scoreboard, SearchAndDestroyScoreboard
        ):
            raise ValueError(
                "Scoreboard must be of type SearchAndDestroyScoreboard for Search and Destroy mode"
            )

        return self


class MatchDocument(BaseModel):
    discord_user_id: int = Field(
        ..., description="Discord user ID associated with the match"
    )
    discord_message_id: int = Field(
        ..., description="Discord message ID associated with the match"
    )
    discord_channel_id: int = Field(
        ..., description="Discord channel ID associated with the match"
    )
    game_stats: GameStatsResponse = Field(..., description="Game stats response object")
    created_at: datetime = Field(
        ..., description="Timestamp when the match was saved to MongoDB"
    )

ALLOWED_AGGREGATION_OPERATORS = Literal["$match", "$group", "$project", "$sort", "$limit", "$skip", "$unwind"]
class MongoStage(BaseModel):
    """Model for MongoDB stage documents"""

    operator: ALLOWED_AGGREGATION_OPERATORS = Field(..., description="MongoDB aggregation operator")
    expression: Dict[str, Any] = Field(
        ..., description="Expression for the aggregation operator"
    )


class MongoPipeline(BaseModel):
    """Model for MongoDB aggregation pipelines"""

    stages: List[MongoStage] = Field(
        ..., description="List of MongoDB aggregation stages"
    )
