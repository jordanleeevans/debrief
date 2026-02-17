import pytest
from app.shared.models.schemas import MatchDocument, MongoPipeline
from app.tests.mocks import FakeMatchRepository, FakeGeminiClient


class TestMatchRepositoryInit:
    """Test MatchRepository initialization"""

    def test_init_creates_empty_matches(self):
        """Test that MatchRepository initializes with empty matches"""
        repository = FakeMatchRepository()

        assert repository.matches == []


class TestMatchRepositoryInsertOne:
    """Test MatchRepository insert_one method"""

    @pytest.mark.asyncio
    async def test_insert_one_valid_document(self):
        """Test inserting a valid MatchDocument"""
        repository = FakeMatchRepository()

        game_stats = await FakeGeminiClient().generate_game_stats(b"test", b"test")
        from datetime import datetime, timezone

        match_doc = MatchDocument(
            discord_user_id=123,
            discord_message_id=456,
            discord_channel_id=789,
            game_stats=game_stats,
            created_at=datetime.now(timezone.utc),
        )

        result = await repository.insert_one(match_doc)

        assert result is not None
        assert isinstance(result, str)
        assert len(repository.matches) == 1

    @pytest.mark.asyncio
    async def test_insert_one_invalid_type_raises_error(self):
        """Test that inserting a non-MatchDocument raises ValueError"""
        repository = FakeMatchRepository()

        with pytest.raises(ValueError) as exc_info:
            await repository.insert_one({"not": "a match document"})

        assert "must be an instance of MatchDocument" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_insert_one_dict_raises_error(self):
        """Test that inserting a dict raises ValueError"""
        repository = FakeMatchRepository()

        with pytest.raises(ValueError) as exc_info:
            await repository.insert_one({})

        assert "must be an instance of MatchDocument" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_insert_one_none_raises_error(self):
        """Test that inserting None raises ValueError"""
        repository = FakeMatchRepository()

        with pytest.raises(ValueError) as exc_info:
            await repository.insert_one(None)

        assert "must be an instance of MatchDocument" in str(exc_info.value)


class TestMatchRepositoryAggregate:
    """Test MatchRepository aggregate method"""

    @pytest.mark.asyncio
    async def test_aggregate_with_valid_pipeline(self):
        """Test running an aggregation with a valid pipeline"""
        repository = FakeMatchRepository()

        pipeline = {
            "stages": [{"operator": "$match", "expression": {"discord_user_id": 123}}]
        }

        result = await repository.aggregate(pipeline)

        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_aggregate_validates_pipeline(self):
        """Test that aggregate validates the pipeline"""
        repository = FakeMatchRepository()

        # Invalid pipeline - missing required fields
        invalid_pipeline = {"invalid": "structure"}

        with pytest.raises(Exception):  # Pydantic validation error
            await repository.aggregate(invalid_pipeline)

    @pytest.mark.asyncio
    async def test_aggregate_with_multiple_stages(self):
        """Test aggregation with multiple pipeline stages"""
        repository = FakeMatchRepository()

        pipeline = {
            "stages": [
                {"operator": "$match", "expression": {"discord_user_id": 123}},
                {"operator": "$sort", "expression": {"created_at": -1}},
                {"operator": "$limit", "expression": 10},
            ]
        }

        result = await repository.aggregate(pipeline)

        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_aggregate_with_pydantic_model(self):
        """Test that aggregate works with MongoPipeline pydantic model"""
        repository = FakeMatchRepository()

        pipeline_model = MongoPipeline(
            stages=[{"operator": "$match", "expression": {"discord_user_id": 456}}]
        )

        result = await repository.aggregate(pipeline_model.model_dump())

        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_aggregate_returns_empty_list_for_no_matches(self):
        """Test that aggregate returns empty list when no documents match"""
        repository = FakeMatchRepository()

        pipeline = {
            "stages": [
                {"operator": "$match", "expression": {"discord_user_id": 999999}}
            ]
        }

        result = await repository.aggregate(pipeline)

        # FakeMatchRepository returns empty list for testing
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_aggregate_complex_pipeline(self):
        """Test aggregate with a complex multi-stage pipeline"""
        repository = FakeMatchRepository()

        pipeline = {
            "stages": [
                {
                    "operator": "$match",
                    "expression": {"game_stats.game_mode": "HARDPOINT"},
                },
                {
                    "operator": "$group",
                    "expression": {
                        "_id": "$discord_user_id",
                        "total_matches": {"$sum": 1},
                    },
                },
                {"operator": "$sort", "expression": {"total_matches": -1}},
                {"operator": "$limit", "expression": 5},
            ]
        }

        result = await repository.aggregate(pipeline)

        assert isinstance(result, list)
