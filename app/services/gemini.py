from google import genai
from google.genai import types
from app.models.schemas import GameStatsResponse

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
