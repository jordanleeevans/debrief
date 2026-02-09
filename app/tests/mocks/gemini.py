from app.models.schemas import GameStatsResponse
from app.services.gemini import GeminiClient
from app.models.enums import AssaultRifles, Pistols, Maps, GameModes, Teams
from app.models.schemas import (
    PrimaryWeaponStats,
    SecondaryWeaponStats,
    MeleeWeaponStats,
    HardpointScoreboard,
)


class FakeGeminiClient(GeminiClient):

    def __call__(self, api_key: str = None):
        return self

    def __init__(self, api_key: str = None):
        pass

    async def generate_db_query(self, prompt) -> dict:
        # Return a fake MongoDB pipeline as a dict (not JSON string)
        return {
            "stages": [{"operator": "$match", "expression": {"discord_user_id": 123}}]
        }

    async def generate_game_stats(
        self, image_one: bytes, image_two: bytes | None = None
    ) -> GameStatsResponse:
        # Return fake data for testing purposes
        return GameStatsResponse(
            primary_weapon_stats=PrimaryWeaponStats(
                primary_weapon_name=AssaultRifles.M15_MOD_0,
                eliminations=50,
                elimination_death_ratio=2.5,
                damage_dealt=5000,
                headshot_kills=20,
                headshot_percentage=40.0,
                accuracy_percentage=30.0,
            ),
            secondary_weapon_stats=SecondaryWeaponStats(
                secondary_weapon_name=Pistols.JAEGER_45,
                eliminations=20,
                elimination_death_ratio=1.0,
                damage_dealt=2000,
                headshot_kills=5,
                headshot_percentage=25.0,
                accuracy_percentage=20.0,
            ),
            melee_weapon_stats=MeleeWeaponStats(
                melee_weapon_name="Combat Knife",
                kill_death_ratio=3.0,
                damage_dealt=300,
            ),
            map=Maps.SCAR,
            game_mode=GameModes.HARDPOINT,
            team=Teams.GUILD,
            scoreboard=HardpointScoreboard(
                player="FakePlayer",
                eliminations=50,
                deaths=25,
                elimination_death_ratio=2.0,
                score=10000,
                time=1200,
                objective_captures=5,
                objective_kills=15,
                captures=3,
                friendly_score=150,
                enemy_score=100,
            ),
        )
