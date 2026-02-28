"""Tests for analyze_responses function."""
import pytest
from src.server import analyze_responses


class TestAnalyzeResponses:
    """Tests for analyze_responses function."""

    @pytest.fixture
    def successful_responses(self):
        """Fixture with successful responses from multiple platforms."""
        return [
            {
                "platform": "zhipu",
                "response": {"text": "Artificial intelligence is..."},
                "elapsed_time": 2.5,
                "status": "success"
            },
            {
                "platform": "qwen",
                "response": {"text": "AI stands for Artificial Intelligence."},
                "elapsed_time": 3.0,
                "status": "success"
            },
        ]

    @pytest.fixture
    def mixed_responses(self):
        """Fixture with mixed success and error responses."""
        return [
            {
                "platform": "zhipu",
                "response": {"text": "This is a response."},
                "elapsed_time": 2.0,
                "status": "success"
            },
            {
                "platform": "qwen",
                "response": {"error": "Network timeout"},
                "elapsed_time": 1.0,
                "status": "error"
            },
            {
                "platform": "kimi",
                "response": {"text": "Another response here."},
                "elapsed_time": 4.0,
                "status": "success"
            },
        ]

    @pytest.mark.asyncio
    async def test_analyze_all_successful(self, successful_responses):
        """Test analysis when all responses are successful."""
        result = await analyze_responses(successful_responses)

        assert result["total_platforms"] == 2
        assert result["successful"] == 2
        assert result["failed"] == 0

    @pytest.mark.asyncio
    async def test_analyze_mixed_results(self, mixed_responses):
        """Test analysis with mixed success and error responses."""
        result = await analyze_responses(mixed_responses)

        assert result["total_platforms"] == 3
        assert result["successful"] == 2
        assert result["failed"] == 1

    @pytest.mark.asyncio
    async def test_analyze_response_length(self, successful_responses):
        """Test that response length is calculated correctly."""
        result = await analyze_responses(successful_responses)

        zhipu_data = next(p for p in result["platforms"] if p["platform"] == "zhipu")
        assert zhipu_data["response_length"] == len("Artificial intelligence is...")
        # "Artificial intelligence is..." has 3 words when split
        assert zhipu_data["word_count"] == 3

    @pytest.mark.asyncio
    async def test_analyze_word_count(self):
        """Test word count calculation."""
        responses = [
            {
                "platform": "test",
                "response": {"text": "One two three four five"},
                "elapsed_time": 1.0,
                "status": "success"
            }
        ]
        result = await analyze_responses(responses)

        platform_data = result["platforms"][0]
        assert platform_data["word_count"] == 5

    @pytest.mark.asyncio
    async def test_analyze_error_response(self):
        """Test analysis of error responses."""
        responses = [
            {
                "platform": "failed_platform",
                "response": {"error": "Something went wrong"},
                "elapsed_time": 0.5,
                "status": "error"
            }
        ]
        result = await analyze_responses(responses)

        assert result["total_platforms"] == 1
        assert result["successful"] == 0
        assert result["failed"] == 1

        platform_data = result["platforms"][0]
        assert platform_data["error"] == "Something went wrong"
        assert "response_length" not in platform_data

    @pytest.mark.asyncio
    async def test_analyze_empty_responses(self):
        """Test analysis with empty response list."""
        result = await analyze_responses([])

        assert result["total_platforms"] == 0
        assert result["successful"] == 0
        assert result["failed"] == 0
        assert result["platforms"] == []

    @pytest.mark.asyncio
    async def test_platforms_list_order(self, mixed_responses):
        """Test that platforms are in correct order."""
        result = await analyze_responses(mixed_responses)

        platforms = [p["platform"] for p in result["platforms"]]
        assert platforms == ["zhipu", "qwen", "kimi"]
