"""Tests for cookie management functions."""
import json
import os
import pytest
from unittest.mock import patch, mock_open, MagicMock

from src.server import (
    load_cookies,
    save_cookies,
    COOKIE_DIR,
    Platform,
)


class TestLoadCookies:
    """Tests for load_cookies function."""

    @pytest.fixture
    def mock_cookies(self):
        """Fixture with mock cookie data."""
        return [
            {"name": "session_id", "value": "abc123"},
            {"name": "user_token", "value": "xyz789"}
        ]

    @pytest.mark.asyncio
    async def test_load_cookies_file_exists(self, mock_cookies, tmp_path):
        """Test loading cookies when file exists."""
        platform = Platform.ZHIPU
        cookie_file = tmp_path / f"{platform.value}.json"

        with patch("src.server.COOKIE_DIR", str(tmp_path)):
            with open(cookie_file, "w") as f:
                json.dump(mock_cookies, f)

            result = await load_cookies(platform)

            assert result == mock_cookies

    @pytest.mark.asyncio
    async def test_load_cookies_file_not_exists(self, tmp_path):
        """Test loading cookies when file doesn't exist."""
        platform = Platform.ZHIPU

        with patch("src.server.COOKIE_DIR", str(tmp_path)):
            result = await load_cookies(platform)

            assert result is None

    @pytest.mark.asyncio
    async def test_load_cookies_invalid_json(self, tmp_path):
        """Test loading cookies with invalid JSON raises error."""
        platform = Platform.ZHIPU
        cookie_file = tmp_path / f"{platform.value}.json"

        with patch("src.server.COOKIE_DIR", str(tmp_path)):
            with open(cookie_file, "w") as f:
                f.write("invalid json {")

            # The current implementation raises JSONDecodeError on invalid JSON
            with pytest.raises(Exception):
                await load_cookies(platform)

    @pytest.mark.asyncio
    async def test_load_cookies_different_platforms(self, mock_cookies, tmp_path):
        """Test loading cookies for different platforms."""
        with patch("src.server.COOKIE_DIR", str(tmp_path)):
            # Create cookie files for different platforms
            for platform in [Platform.ZHIPU, Platform.QWEN, Platform.KIMI, Platform.MINIMAX]:
                cookie_file = tmp_path / f"{platform.value}.json"
                with open(cookie_file, "w") as f:
                    json.dump(mock_cookies, f)

                result = await load_cookies(platform)
                assert result == mock_cookies


class TestSaveCookies:
    """Tests for save_cookies function."""

    @pytest.fixture
    def mock_cookies(self):
        """Fixture with mock cookie data."""
        return [
            {"name": "session_id", "value": "abc123"},
            {"name": "user_token", "value": "xyz789"}
        ]

    @pytest.mark.asyncio
    async def test_save_cookies_creates_directory(self, mock_cookies, tmp_path):
        """Test that save_cookies creates directory if it doesn't exist."""
        platform = Platform.ZHIPU

        with patch("src.server.COOKIE_DIR", str(tmp_path / "cookies")):
            # Directory should not exist initially
            cookie_dir = tmp_path / "cookies"
            assert not cookie_dir.exists()

            await save_cookies(platform, mock_cookies)

            # Directory should now exist
            assert cookie_dir.exists()

    @pytest.mark.asyncio
    async def test_save_cookies_creates_file(self, mock_cookies, tmp_path):
        """Test that save_cookies creates file correctly."""
        platform = Platform.QWEN

        with patch("src.server.COOKIE_DIR", str(tmp_path)):
            await save_cookies(platform, mock_cookies)

            cookie_file = tmp_path / f"{platform.value}.json"
            assert cookie_file.exists()

            with open(cookie_file) as f:
                saved_data = json.load(f)

            assert saved_data == mock_cookies

    @pytest.mark.asyncio
    async def test_save_cookies_overwrites_existing(self, mock_cookies, tmp_path):
        """Test that save_cookies overwrites existing file."""
        platform = Platform.KIMI
        new_cookies = [{"name": "new_session", "value": "new_value"}]

        with patch("src.server.COOKIE_DIR", str(tmp_path)):
            # First save
            await save_cookies(platform, mock_cookies)

            # Second save with different data
            await save_cookies(platform, new_cookies)

            cookie_file = tmp_path / f"{platform.value}.json"
            with open(cookie_file) as f:
                saved_data = json.load(f)

            assert saved_data == new_cookies

    @pytest.mark.asyncio
    async def test_save_cookies_different_platforms(self, mock_cookies, tmp_path):
        """Test saving cookies for different platforms."""
        with patch("src.server.COOKIE_DIR", str(tmp_path)):
            for platform in [Platform.ZHIPU, Platform.QWEN, Platform.KIMI, Platform.MINIMAX]:
                await save_cookies(platform, mock_cookies)

                cookie_file = tmp_path / f"{platform.value}.json"
                assert cookie_file.exists()

                with open(cookie_file) as f:
                    assert json.load(f) == mock_cookies


class TestCookieIntegration:
    """Integration tests for cookie operations."""

    @pytest.mark.asyncio
    async def test_save_and_load_roundtrip(self, tmp_path):
        """Test that cookies can be saved and loaded correctly."""
        platform = Platform.MINIMAX
        original_cookies = [
            {"name": "test", "value": "value123", "domain": ".example.com"}
        ]

        with patch("src.server.COOKIE_DIR", str(tmp_path)):
            await save_cookies(platform, original_cookies)
            loaded_cookies = await load_cookies(platform)

            assert loaded_cookies == original_cookies
