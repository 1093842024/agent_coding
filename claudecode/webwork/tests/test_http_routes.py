"""Tests for HTTP custom routes: /query, /status, /fetch-replies, /health, /."""
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Import after patching so we can set http_state
from starlette.testclient import TestClient


def test_reply_extraction_js_merge_and_last():
    """Reply extraction uses merge-and-last strategy and prefers nodes with substantial text."""
    from src.server import _reply_text_js_merge_and_last, REPLY_MIN_TEXT_LEN

    js = _reply_text_js_merge_and_last(["[data-role='assistant']", ".markdown-body"])
    assert "querySelectorAll" in js
    assert "compareDocumentPosition" in js
    assert "nodes.length" in js
    assert "DOCUMENT_POSITION_FOLLOWING" in js
    assert str(REPLY_MIN_TEXT_LEN) in js


def test_reply_extraction_js_per_platform():
    """Each platform has non-empty reply extraction JS."""
    from src.server import _reply_text_js_for_platform

    for pid in ("zhipu", "qwen", "kimi", "minimax"):
        js = _reply_text_js_for_platform(pid)
        assert isinstance(js, str)
        assert len(js) > 100
        assert "querySelectorAll" in js


@pytest.fixture
def mock_http_state_none():
    """No browser state (e.g. server just started or stdio mode)."""
    with patch("src.server.http_state", None):
        yield


@pytest.fixture
def mock_http_state_ready():
    """Browser and pages ready."""
    state = MagicMock()
    state.pages = {"zhipu": MagicMock(), "qwen": MagicMock(), "kimi": MagicMock(), "minimax": MagicMock()}
    for p in state.pages.values():
        p.is_closed = MagicMock(return_value=False)
    state.reply_statuses = {"zhipu": "done", "qwen": "done", "kimi": "waiting", "minimax": "replying"}
    state._lock = MagicMock()
    state._lock.__aenter__ = AsyncMock(return_value=None)
    state._lock.__aexit__ = AsyncMock(return_value=None)
    state.last_question = "test question"
    state.browser = MagicMock()
    state.context = MagicMock()
    with patch("src.server.http_state", state):
        yield state


def get_app():
    from src.server import mcp
    return mcp.streamable_http_app()


@pytest.mark.asyncio
async def test_health_returns_ok():
    """GET /health returns 200 and status ok."""
    with patch("src.server.http_state", None):
        app = get_app()
        client = TestClient(app)
        resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "browser_ready" in data


@pytest.mark.asyncio
async def test_health_browser_ready():
    """GET /health reports browser_ready when state exists."""
    state = MagicMock()
    state.browser = MagicMock()
    with patch("src.server.http_state", state):
        app = get_app()
        client = TestClient(app)
        resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json().get("browser_ready") is True


@pytest.mark.asyncio
async def test_query_without_browser_returns_503(mock_http_state_none):
    """POST /query when browser not ready returns 503."""
    app = get_app()
    client = TestClient(app)
    resp = client.post("/query", json={"question": "hello", "platforms": ["zhipu"]})
    assert resp.status_code == 503
    data = resp.json()
    assert data.get("ok") is False
    assert "error" in data


@pytest.mark.asyncio
async def test_query_missing_question_returns_400(mock_http_state_ready):
    """POST /query without question returns 400."""
    app = get_app()
    client = TestClient(app)
    resp = client.post("/query", json={"platforms": ["zhipu"]})
    assert resp.status_code == 400
    data = resp.json()
    assert data.get("ok") is False
    assert "question" in data.get("error", "").lower()


@pytest.mark.asyncio
async def test_status_returns_platforms_and_question(mock_http_state_ready):
    """GET /status returns platforms and question."""
    app = get_app()
    client = TestClient(app)
    resp = client.get("/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "platforms" in data
    assert "question" in data
    assert data["question"] == "test question"
    # REPLY_STATUS maps internal keys to Chinese labels
    assert any("完成" in str(v) or "等待" in str(v) or "回复" in str(v) or "发送" in str(v) for v in data["platforms"].values())


@pytest.mark.asyncio
async def test_status_no_state_returns_empty():
    """GET /status when no state returns empty platforms."""
    with patch("src.server.http_state", None):
        app = get_app()
        client = TestClient(app)
        resp = client.get("/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("platforms") == {}
    assert data.get("question") is None


@pytest.mark.asyncio
async def test_fetch_replies_without_browser_returns_503(mock_http_state_none):
    """POST /fetch-replies when browser not ready returns 503."""
    app = get_app()
    client = TestClient(app)
    resp = client.post("/fetch-replies")
    assert resp.status_code == 503
    data = resp.json()
    assert data.get("ok") is False


@pytest.mark.asyncio
async def test_fetch_replies_returns_ok_and_responses(mock_http_state_ready):
    """POST /fetch-replies returns ok and responses when browser ready."""
    async def fake_get_latest_reply(page, pid):
        return {"text": f"reply from {pid}", "error": None}

    with patch("src.server.get_latest_reply", side_effect=fake_get_latest_reply):
        app = get_app()
        client = TestClient(app)
        resp = client.post("/fetch-replies")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("ok") is True
    assert "responses" in data
    assert len(data["responses"]) == 4
    assert data.get("question") == "test question"
    for r in data["responses"]:
        assert "platform" in r
        assert "text" in r
        assert "status" in r


@pytest.mark.asyncio
async def test_fetch_replies_hello_returns_correct_model_replies(mock_http_state_ready):
    """With question 'hello', fetch-replies returns correct model reply text for each platform."""
    mock_http_state_ready.last_question = "hello"
    hello_replies = {
        "zhipu": "你好！我是智谱AI助手，有什么可以帮你的？",
        "qwen": "你好呀！我是通义千问，很高兴为你服务。",
        "kimi": "Hello！我是Kimi，有什么想问的？",
        "minimax": "你好，我是MiniMax，请问有什么可以帮您？",
    }

    async def fake_get_latest_reply(page, pid):
        text = hello_replies.get(pid, "")
        return {"text": text, "error": None}

    with patch("src.server.get_latest_reply", side_effect=fake_get_latest_reply):
        app = get_app()
        client = TestClient(app)
        resp = client.post("/fetch-replies")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("ok") is True
    assert data.get("question") == "hello"
    for r in data["responses"]:
        pid = r["platform"]
        assert r["status"] == "success"
        assert r["text"] == hello_replies.get(pid, "")
        assert len(r["text"]) > 5


@pytest.mark.asyncio
async def test_serve_compare_page_returns_html():
    """GET / returns comparison page HTML or 404."""
    app = get_app()
    client = TestClient(app)
    resp = client.get("/")
    # If frontend/index.html exists we get 200 and HTML
    if resp.status_code == 200:
        assert "text/html" in resp.headers.get("content-type", "")
        assert b"<!DOCTYPE" in resp.content or b"<html" in resp.content
    else:
        assert resp.status_code == 404
