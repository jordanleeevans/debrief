from google import genai
from google.genai import types
from app.models.schemas import GameStatsResponse, MongoPipeline, MatchDocument

MATCH_ANALYSIS_PROMPT = """
Here are two images of a player in Call of Duty: Black ops 7.
The first image is a screenshot of the player's end-of-game stats,
and the second image is a screenshot of the player's weapon stats.
Extract the relevant information for the highlighted player on
the scoreboard. Be careful to distinguish zeros and eights, since
the zeros tend to have a dot in the middle of them. 
"""

DB_QUERY_PROMPT = """
You are a PyMongo and MongoDB analytics expert.

The collection contains match documents with the following schema:

```json
%s
```

Rules:
- One document = one match
- You follow MongoDB aggregation syntax that PyMongo uses in Python, but you output only the stages as a JSON array.
- Use field paths exactly as defined
- Do NOT invent any fields that are not defined in the schema
- Only use the fields defined in the schema for your queries
- Always use the correct scoreboard type for the game mode (HardpointScoreboard for Hardpoint, etc.)
- Output only the MongoDB aggregation pipeline stages as a JSON array, without any additional text or explanation. The output should be directly usable in a MongoDB aggregate() function.
- Allowed aggregation operators are: $match, $group, $project, $sort, $limit, $skip, and $unwind.
- No writes, deletes, or updates - only reads using aggregation pipelines.

Generate a MongoDB aggregation pipeline based on the following user request:
""" % (
    MatchDocument.model_json_schema()
)


class GeminiClient:
    model = "gemini-2.5-flash-lite"

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
                model=self.model,
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
            MATCH_ANALYSIS_PROMPT,
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

    async def generate_db_query(self, prompt: str) -> dict:
        async with self.client.aio as aclient:
            response = await aclient.models.generate_content(
                model=self.model,
                contents=DB_QUERY_PROMPT + prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_json_schema=MongoPipeline.model_json_schema(),
                ),
            )
            return response.model_dump_json()
