"""Tests for Pydantic input models."""
import pytest
from pydantic import ValidationError

from src.server import (
    CompareLLMsInput,
    SingleQueryInput,
    LoginStatusInput,
    Platform,
    ResponseFormat,
)


class TestPlatformEnum:
    """Tests for Platform enum."""

    def test_platform_enum_values(self):
        """Verify Platform enum has correct values."""
        assert Platform.ZHIPU.value == "zhipu"
        assert Platform.QWEN.value == "qwen"
        assert Platform.KIMI.value == "kimi"
        assert Platform.MINIMAX.value == "minimax"

    def test_platform_enum_members(self):
        """Verify all expected platforms exist."""
        platforms = list(Platform)
        assert len(platforms) == 4
        assert Platform.ZHIPU in platforms
        assert Platform.QWEN in platforms
        assert Platform.KIMI in platforms
        assert Platform.MINIMAX in platforms


class TestResponseFormatEnum:
    """Tests for ResponseFormat enum."""

    def test_response_format_values(self):
        """Verify ResponseFormat enum has correct values."""
        assert ResponseFormat.MARKDOWN.value == "markdown"
        assert ResponseFormat.JSON.value == "json"


class TestCompareLLMsInput:
    """Tests for CompareLLMsInput model."""

    def test_valid_input_with_all_fields(self):
        """Test valid input with all fields provided."""
        input_data = CompareLLMsInput(
            question="What is AI?",
            platforms=[Platform.ZHIPU, Platform.QWEN],
            response_format=ResponseFormat.JSON
        )
        assert input_data.question == "What is AI?"
        assert len(input_data.platforms) == 2
        assert input_data.response_format == ResponseFormat.JSON

    def test_valid_input_minimal(self):
        """Test valid input with only required field."""
        input_data = CompareLLMsInput(question="Hello world")
        assert input_data.question == "Hello world"
        assert input_data.platforms is None
        assert input_data.response_format == ResponseFormat.MARKDOWN

    def test_question_required(self):
        """Test that question field is required."""
        with pytest.raises(ValidationError) as exc_info:
            CompareLLMsInput()
        assert "question" in str(exc_info.value)

    def test_question_min_length(self):
        """Test question minimum length validation."""
        with pytest.raises(ValidationError):
            CompareLLMsInput(question="")

    def test_question_max_length(self):
        """Test question maximum length validation."""
        long_question = "a" * 5001
        with pytest.raises(ValidationError):
            CompareLLMsInput(question=long_question)

    def test_question_whitespace_stripping(self):
        """Test that whitespace is stripped from question."""
        input_data = CompareLLMsInput(question="  Hello World  ")
        assert input_data.question == "Hello World"

    def test_platforms_default_none(self):
        """Test that platforms defaults to None."""
        input_data = CompareLLMsInput(question="Test?")
        assert input_data.platforms is None

    def test_response_format_default_markdown(self):
        """Test that response_format defaults to MARKDOWN."""
        input_data = CompareLLMsInput(question="Test?")
        assert input_data.response_format == ResponseFormat.MARKDOWN


class TestSingleQueryInput:
    """Tests for SingleQueryInput model."""

    def test_valid_input(self):
        """Test valid input."""
        input_data = SingleQueryInput(
            platform=Platform.KIMI,
            question="What is machine learning?"
        )
        assert input_data.platform == Platform.KIMI
        assert input_data.question == "What is machine learning?"

    def test_platform_required(self):
        """Test that platform field is required."""
        with pytest.raises(ValidationError):
            SingleQueryInput(question="Test?")

    def test_question_required(self):
        """Test that question field is required."""
        with pytest.raises(ValidationError):
            SingleQueryInput(platform=Platform.ZHIPU)

    def test_question_min_length(self):
        """Test question minimum length validation."""
        with pytest.raises(ValidationError):
            SingleQueryInput(platform=Platform.ZHIPU, question="")

    def test_question_max_length(self):
        """Test question maximum length validation."""
        long_question = "a" * 5001
        with pytest.raises(ValidationError):
            SingleQueryInput(platform=Platform.ZHIPU, question=long_question)


class TestLoginStatusInput:
    """Tests for LoginStatusInput model."""

    def test_valid_input_with_platform(self):
        """Test valid input with specific platform."""
        input_data = LoginStatusInput(platform=Platform.MINIMAX)
        assert input_data.platform == Platform.MINIMAX

    def test_valid_input_without_platform(self):
        """Test valid input without platform (checks all)."""
        input_data = LoginStatusInput()
        assert input_data.platform is None

    def test_platform_default_none(self):
        """Test that platform defaults to None."""
        input_data = LoginStatusInput()
        assert input_data.platform is None
