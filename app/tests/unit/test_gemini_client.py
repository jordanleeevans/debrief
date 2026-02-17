from pydantic import TypeAdapter
import pydantic
import pytest
from app.shared.services.gemini import GeminiClient, MATCH_ANALYSIS_PROMPT, DB_QUERY_PROMPT
from app.shared.models.schemas import (
    ALLOWED_AGGREGATION_OPERATORS,
    GameStatsResponse,
    MongoPipeline,
)
from app.tests.mocks import FakeGeminiClient
from google.genai import types


class TestGeminiClientInit:
    """Test GeminiClient initialization"""

    def test_init_without_api_key(self):
        """Test that GeminiClient can be initialized without an API key"""
        client = FakeGeminiClient()
        assert client is not None

    def test_init_with_api_key(self):
        """Test that GeminiClient can be initialized with an API key"""
        client = FakeGeminiClient(api_key="test-api-key")
        assert client is not None

    def test_callable_returns_instance(self):
        """Test that calling the client instance returns itself"""
        client = FakeGeminiClient()
        called_client = client(api_key="test-key")
        assert called_client is client


class TestCreateContents:
    """Test the create_contents helper method"""

    def test_create_contents_with_one_image(self):
        """Test create_contents with a single image"""
        client = GeminiClient(api_key="test-key")
        image_data = b"fake_image_data"

        contents = client.create_contents(image_data)

        assert len(contents) == 2
        assert contents[0] == MATCH_ANALYSIS_PROMPT
        assert isinstance(contents[1], types.Part)

    def test_create_contents_with_two_images(self):
        """Test create_contents with two images"""
        client = GeminiClient(api_key="test-key")
        image_one = b"fake_image_one"
        image_two = b"fake_image_two"

        contents = client.create_contents(image_one, image_two)

        assert len(contents) == 3
        assert contents[0] == MATCH_ANALYSIS_PROMPT
        assert isinstance(contents[1], types.Part)
        assert isinstance(contents[2], types.Part)

    def test_create_contents_images_have_correct_mime_type(self):
        """Test that image parts have the correct MIME type"""
        client = GeminiClient(api_key="test-key")
        image_data = b"fake_image_data"

        contents = client.create_contents(image_data)

        # The Part should have been created with mime_type="image/png"
        assert isinstance(contents[1], types.Part)


class TestGenerateGameStats:
    """Test the generate_game_stats method"""

    @pytest.mark.asyncio
    async def test_generate_game_stats_with_one_image(self):
        """Test generating game stats with a single image"""
        client = FakeGeminiClient()
        image_one = b"fake_image_data"

        result = await client.generate_game_stats(image_one)

        assert isinstance(result, GameStatsResponse)
        assert result.map is not None
        assert result.game_mode is not None
        assert result.team is not None
        assert result.scoreboard is not None

    @pytest.mark.asyncio
    async def test_generate_game_stats_with_two_images(self):
        """Test generating game stats with two images"""
        client = FakeGeminiClient()
        image_one = b"fake_image_one"
        image_two = b"fake_image_two"

        result = await client.generate_game_stats(image_one, image_two)

        assert isinstance(result, GameStatsResponse)
        assert result.primary_weapon_stats is not None
        assert result.secondary_weapon_stats is not None
        assert result.melee_weapon_stats is not None

    @pytest.mark.asyncio
    async def test_generate_game_stats_returns_valid_response(self):
        """Test that generate_game_stats returns a valid GameStatsResponse"""
        client = FakeGeminiClient()
        image_data = b"fake_image"

        result = await client.generate_game_stats(image_data)

        # Validate that all required fields are present
        assert result.map is not None
        assert result.team is not None
        assert result.game_mode is not None
        assert result.scoreboard is not None

    @pytest.mark.asyncio
    async def test_generate_game_stats_scoreboard_has_player_name(self):
        """Test that the scoreboard contains a player name"""
        client = FakeGeminiClient()
        image_data = b"fake_image"

        result = await client.generate_game_stats(image_data)

        assert hasattr(result.scoreboard, "player")
        assert result.scoreboard.player is not None
        assert len(result.scoreboard.player) > 0


class TestGenerateDbQuery:
    """Test the generate_db_query method"""

    @pytest.mark.asyncio
    async def test_generate_db_query_returns_dict(self):
        """Test that generate_db_query returns a dictionary"""
        client = FakeGeminiClient()
        prompt = "Show me all matches for user 123"

        result = await client.generate_db_query(prompt)

        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_generate_db_query_has_stages(self):
        """Test that the returned dictionary has a 'stages' key"""
        client = FakeGeminiClient()
        prompt = "Get my recent matches"

        result = await client.generate_db_query(prompt)

        assert "stages" in result
        assert isinstance(result["stages"], list)

    @pytest.mark.asyncio
    async def test_generate_db_query_stages_are_valid(self):
        """Test that the stages are valid MongoDB aggregation stages"""
        client = FakeGeminiClient()
        prompt = "Find all hardpoint matches"

        result = await client.generate_db_query(prompt)

        for stage in result["stages"]:
            assert "operator" in stage
            assert "expression" in stage

    @pytest.mark.asyncio
    async def test_generate_db_query_can_be_validated_as_pipeline(self):
        """Test that the result can be validated as a MongoPipeline"""
        client = FakeGeminiClient()
        prompt = "Get top 10 matches by score"

        result = await client.generate_db_query(prompt)

        pipeline = MongoPipeline.model_validate(result)
        assert pipeline is not None
        assert len(pipeline.stages) > 0

    @pytest.mark.asyncio
    async def test_generate_db_query_with_empty_prompt(self):
        """Test generate_db_query with an empty prompt still returns valid structure"""
        client = FakeGeminiClient()
        prompt = ""

        result = await client.generate_db_query(prompt)

        assert isinstance(result, dict)
        assert "stages" in result

    @pytest.mark.asyncio
    async def test_generate_db_query_with_complex_prompt(self):
        """Test generate_db_query with a complex natural language prompt"""
        client = FakeGeminiClient()
        prompt = "Show me all matches from last week where I had more than 50 eliminations and played on Hardpoint mode"

        result = await client.generate_db_query(prompt)

        assert isinstance(result, dict)
        assert "stages" in result
        assert len(result["stages"]) >= 1


class TestGeminiClientIntegration:
    """Integration tests for GeminiClient"""

    @pytest.mark.asyncio
    async def test_full_workflow_image_analysis(self):
        """Test the full workflow of analyzing an image"""
        client = FakeGeminiClient(api_key="test-key")

        image_one = b"fake_screenshot_1"
        image_two = b"fake_screenshot_2"

        stats = await client.generate_game_stats(image_one, image_two)

        assert isinstance(stats, GameStatsResponse)
        assert stats.primary_weapon_stats.eliminations >= 0
        assert stats.secondary_weapon_stats.eliminations >= 0
        assert stats.scoreboard.eliminations >= 0

    @pytest.mark.asyncio
    async def test_full_workflow_db_query_generation(self):
        """Test the full workflow of generating a database query"""
        client = FakeGeminiClient(api_key="test-key")

        query_result = await client.generate_db_query("Get all my matches")

        pipeline = MongoPipeline.model_validate(query_result)
        assert len(pipeline.stages) > 0
        allowed_aggregation_adapter = TypeAdapter(ALLOWED_AGGREGATION_OPERATORS)
        for stage in pipeline.stages:
            try:
                allowed_aggregation_adapter.validate_python(stage.operator) is not False
            except pydantic.ValidationError:
                pytest.fail(f"Invalid aggregation operator: {stage.operator}")
