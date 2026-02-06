from google import genai
from google.genai import types
from app.models.enums import AssaultRifles, Pistols, Maps, GameModes, Teams
from app.models.schemas import (
    GameStatsResponse,
    PrimaryWeaponStats,
    SecondaryWeaponStats,
    MeleeWeaponStats,
    HardpointScoreboard,
)

PROMPT = """
Here are two images of a player in Call of Duty: Black ops 7.
The first image is a screenshot of the player's end-of-game stats,
and the second image is a screenshot of the player's weapon stats.
Extract the relevant information for the highlighted player on
the scoreboard. Be careful to distinguish zeros and eights, since
the zeros tend to have a dot in the middle of them. 
"""


class GeminiClient:
    def __init__(self, api_key: str = None):
        if api_key is None:
            self.client = genai.Client()
        else:
            self.client = genai.Client(api_key=api_key)

    async def generate_game_stats(
        self, image_one: bytes, image_two: bytes | None = None
    ) -> GameStatsResponse:
        async with self.client.aio as aclient:
            response = await aclient.models.generate_content(
                model="gemini-2.5-flash",
                contents=self.create_contents(image_one, image_two),
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=GameStatsResponse.model_json_schema(),
                ),
            )
            return GameStatsResponse.model_validate_json(response.text)

    def create_contents(
        self, image_one: bytes, image_two: bytes | None = None
    ) -> list[types.Part | str]:
        contents = [
            PROMPT,
            types.Part.from_bytes(
                data=image_one,
                mime_type="image/png",
            ),
        ]
        if image_two is not None:
            contents.append(
                types.Part.from_bytes(
                    data=image_two,
                    mime_type="image/png",
                )
            )
        return contents


class FakeGeminiClient(GeminiClient):

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
