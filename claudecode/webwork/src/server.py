#!/usr/bin/env python3
"""
MCP Server for LLM Comparison Tool.

This server provides tools to compare responses from multiple LLM platforms:
- 智谱AI (Zhipu AI)
- 千问 (Qwen/Tongyi)
- Kimi (Moonshot AI)
- MiniMax

When run in HTTP mode: opens one browser with 5 tabs (4 LLM platforms + comparison page),
supports send-question-only, status polling (60s), and fetch-replies for comparison.
"""

import asyncio
import json
import os
import shutil
import subprocess
import sys
import time
from contextlib import asynccontextmanager

import httpx
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field
from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import Response, JSONResponse, FileResponse

# MCP Server created after lifespan (see below)

# Constants
CHARACTER_LIMIT = 25000
COOKIE_DIR = os.path.expanduser("~/.llm_comparison_cookies")
USER_DATA_DIR = os.path.join(COOKIE_DIR, "browser_data")
PLATFORM_URLS = {
    "zhipu": "https://chatglm.cn/",
    "qwen": "https://www.qianwen.com/",
    "kimi": "https://www.kimi.com/",
    "minimax": "https://agent.minimaxi.com/",
}

# Reply status enum for web UI
REPLY_STATUS = {
    "question_sent": "发送问题",
    "waiting": "等待模型响应中",
    "replying": "模型回复中/模型思考中",
    "done": "模型已完成问题回复",
    "error": "错误",
}

# Frontend static path (for serving comparison page)
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

# CDP port for reconnecting to existing browser on restart (do not close browser on exit)
CDP_PORT = 9222


def _chromium_executable() -> Optional[str]:
    """Return path to Chromium/Chrome for detached launch (so browser survives process exit)."""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            path = getattr(p.chromium, "executable_path", None)
            if path and os.path.isfile(path):
                return path
    except Exception:
        pass
    # macOS: Chrome/Chromium are typically in /Applications and not on PATH
    if sys.platform == "darwin":
        for app_name, binary in (
            ("Google Chrome.app", "Google Chrome"),
            ("Chromium.app", "Chromium"),
        ):
            path = f"/Applications/{app_name}/Contents/MacOS/{binary}"
            if os.path.isfile(path):
                return path
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome"):
        path = shutil.which(name)
        if path:
            return path
    return None


def _launch_browser_detached(user_data_dir: str, cdp_port: int) -> bool:
    """Launch Chromium in a detached process so it keeps running after our process exits. Returns True if launched."""
    exe = _chromium_executable()
    if not exe:
        return False
    args = [
        exe,
        f"--user-data-dir={user_data_dir}",
        f"--remote-debugging-port={cdp_port}",
        "--no-first-run",
        "--no-default-browser-check",
    ]
    try:
        if sys.platform == "win32":
            subprocess.Popen(
                args,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=os.path.expanduser("~"),
            )
        else:
            subprocess.Popen(
                args,
                start_new_session=True,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=os.path.expanduser("~"),
            )
        return True
    except Exception:
        return False


# Enums
class ResponseFormat(str, Enum):
    """Output format for tool responses."""
    MARKDOWN = "markdown"
    JSON = "json"


class Platform(str, Enum):
    """Supported LLM platforms."""
    ZHIPU = "zhipu"
    QWEN = "qwen"
    KIMI = "kimi"
    MINIMAX = "minimax"


# Data Models
class CompareLLMsInput(BaseModel):
    """Input model for comparing LLM responses."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    question: str = Field(
        ...,
        description="The question to ask all LLM platforms",
        min_length=1,
        max_length=5000
    )
    platforms: Optional[List[Platform]] = Field(
        default=None,
        description="List of platforms to query. If not specified, all platforms will be queried"
    )
    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable"
    )


class SingleQueryInput(BaseModel):
    """Input model for querying a single platform."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    platform: Platform = Field(
        ...,
        description="The platform to query (zhipu, qwen, kimi, or minimax)"
    )
    question: str = Field(
        ...,
        description="The question to ask",
        min_length=1,
        max_length=5000
    )


class LoginStatusInput(BaseModel):
    """Input model for checking login status."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    platform: Optional[Platform] = Field(
        default=None,
        description="Specific platform to check. If not specified, checks all platforms"
    )


# Global state for HTTP mode: single browser, 5 tabs, reply statuses
@dataclass
class BrowserPool:
    """Manages browser instances for each platform (legacy MCP tools)."""
    browsers: Dict[str, Any] = field(default_factory=dict)
    contexts: Dict[str, Any] = field(default_factory=dict)

    async def init_playwright(self):
        """Initialize Playwright."""
        from playwright.async_api import async_playwright
        self.playwright = await async_playwright().start()

    async def get_browser(self, platform: Platform) -> Any:
        """Get or create browser for platform."""
        if platform not in self.browsers:
            self.browsers[platform] = await self.playwright.chromium.launch(headless=False)
            self.contexts[platform] = await self.browsers[platform].new_context()
        return self.browsers[platform]

    async def close(self):
        """Close all browsers."""
        for browser in self.browsers.values():
            await browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()


@dataclass
class HTTPBrowserState:
    """Single browser with 5 tabs for HTTP mode. Set by lifespan."""
    playwright: Any = None
    browser: Any = None
    context: Any = None
    pages: Dict[str, Any] = field(default_factory=dict)  # platform_id -> page
    compare_page: Any = None
    reply_statuses: Dict[str, str] = field(default_factory=dict)  # platform_id -> status key
    last_question: Optional[str] = None
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)


browser_pool = BrowserPool()
http_state: Optional[HTTPBrowserState] = None


# Cookie Management
async def load_cookies(platform: Platform) -> Optional[List[Dict]]:
    """Load cookies for a platform. Returns list of cookie dicts or None."""
    cookie_file = os.path.join(COOKIE_DIR, f"{platform.value}.json")
    if os.path.exists(cookie_file):
        with open(cookie_file, 'r') as f:
            data = json.load(f)
            return data if isinstance(data, list) else [data]
    return None


def _cookies_with_url(cookies: List[Dict], url: str) -> List[Dict]:
    """Ensure each cookie has 'url' so Playwright applies to the right domain."""
    out = []
    for c in cookies:
        d = dict(c)
        if not d.get("url") and not d.get("domain"):
            d["url"] = url
        out.append(d)
    return out


async def save_cookies(platform: Platform, cookies: List[Dict]) -> None:
    """Save cookies for a platform."""
    os.makedirs(COOKIE_DIR, exist_ok=True)
    cookie_file = os.path.join(COOKIE_DIR, f"{platform.value}.json")
    with open(cookie_file, 'w') as f:
        json.dump(cookies, f)


# ----- Send question only (no wait for reply) -----
async def _send_question_zhipu(page: Any, question: str) -> Optional[str]:
    """Send question to 智谱/ChatGLM page. Tries multiple input/send patterns."""
    try:
        input_selectors = [
            'textarea[placeholder*="请输入"]',
            'textarea[placeholder*="输入"]',
            'textarea[data-testid="chat-input"]',
            'textarea',
            'div[contenteditable="true"][role="textbox"]',
            'div[contenteditable="true"]',
            '[contenteditable="true"]',
        ]
        input_elem = None
        for sel in input_selectors:
            input_elem = await page.query_selector(sel)
            if input_elem:
                break
        if not input_elem:
            return "Could not find input box"
        await input_elem.click()
        await asyncio.sleep(0.2)
        await input_elem.fill("")
        await input_elem.fill(question)
        await asyncio.sleep(0.1)
        send_selectors = [
            'button[type="submit"]',
            'button:has-text("发送")',
            'button:has-text("提交")',
            '[data-testid="send-button"]',
            '[aria-label*="发送"]',
            'button[class*="send"]',
            'button[class*="submit"]',
            'div[class*="send"] button',
            'form button[type="submit"]',
        ]
        for sel in send_selectors:
            btn = await page.query_selector(sel)
            if btn:
                await btn.click()
                return None
        await page.keyboard.press("Enter")
        return None
    except Exception as e:
        return str(e)


async def _send_question_qwen(page: Any, question: str) -> Optional[str]:
    try:
        input_elem = await page.query_selector('textarea[placeholder*="输入"]') or await page.query_selector('div[contenteditable="true"]')
        if not input_elem:
            return "Could not find input box"
        await input_elem.fill(question)
        await page.keyboard.press("Enter")
        return None
    except Exception as e:
        return str(e)


async def _send_question_kimi(page: Any, question: str) -> Optional[str]:
    try:
        for sel in ['textarea[placeholder*="发送"]', 'textarea[placeholder*="输入"]', 'div[contenteditable="true"]']:
            input_elem = await page.query_selector(sel)
            if input_elem:
                await input_elem.fill(question)
                await page.keyboard.press("Enter")
                return None
        return "Could not find input box"
    except Exception as e:
        return str(e)


async def _send_question_minimax(page: Any, question: str) -> Optional[str]:
    try:
        for sel in ['textarea[placeholder*="输入"]', 'textarea[placeholder*="问题"]', 'div[contenteditable="true"]']:
            input_elem = await page.query_selector(sel)
            if input_elem:
                await input_elem.fill(question)
                await page.keyboard.press("Enter")
                return None
        return "Could not find input box"
    except Exception as e:
        return str(e)


async def send_question_to_page(platform_id: str, page: Any, question: str) -> Optional[str]:
    """Send question to a single platform page. Returns error message or None."""
    if platform_id == "zhipu":
        return await _send_question_zhipu(page, question)
    if platform_id == "qwen":
        return await _send_question_qwen(page, question)
    if platform_id == "kimi":
        return await _send_question_kimi(page, question)
    if platform_id == "minimax":
        return await _send_question_minimax(page, question)
    return "Unknown platform"


async def _check_page_logged_in(page: Any) -> bool:
    """Check if the current page appears to be in a logged-in state (user avatar/profile visible)."""
    if not page or page.is_closed():
        return False
    try:
        return await page.evaluate("""() => {
            const indicators = [
                document.querySelector('[data-testid="user-avatar"]'),
                document.querySelector('.user-profile'),
                document.querySelector('[class*="avatar"]'),
                document.querySelector('[class*="nickname"]'),
                document.querySelector('[class*="user-info"]'),
                document.querySelector('img[alt*="头像"]'),
                document.querySelector('img[alt*="avatar"]'),
            ];
            return indicators.some(el => el !== null);
        }""")
    except Exception:
        return False


# ----- Get latest reply text from page (platform-specific selectors) -----
# Min length to consider as a real reply (avoid picking empty or input-like nodes)
REPLY_MIN_TEXT_LEN = 15


def _reply_text_js_merge_and_last(selector_list: List[str]) -> str:
    """Build JS that collects elements matching selectors, merges in doc order, returns last with substantial text."""
    sels_js = ", ".join(json.dumps(s) for s in selector_list)
    min_len = REPLY_MIN_TEXT_LEN
    return f"""
    () => {{
        var sels = [{sels_js}];
        var seen = new Set();
        var nodes = [];
        for (var i = 0; i < sels.length; i++) {{
            try {{
                var list = document.querySelectorAll(sels[i]);
                for (var j = 0; j < list.length; j++) {{
                    var el = list[j];
                    if (!seen.has(el)) {{
                        seen.add(el);
                        nodes.push(el);
                    }}
                }}
            }} catch (e) {{}}
        }}
        if (nodes.length === 0) return '';
        nodes.sort(function(a, b) {{
            var p = a.compareDocumentPosition(b);
            if (p & Node.DOCUMENT_POSITION_FOLLOWING) return -1;
            if (p & Node.DOCUMENT_POSITION_PRECEDING) return 1;
            return 0;
        }});
        for (var i = nodes.length - 1; i >= 0; i--) {{
            var el = nodes[i];
            var text = (el.innerText || el.textContent || '').trim();
            if (text.length >= {min_len}) return text;
        }}
        var last = nodes[nodes.length - 1];
        var text = (last.innerText || last.textContent || '').trim();
        return text || '';
    }}
    """


# Prefer assistant-only selectors first so we don't pick user message or input area
ZHIPU_REPLY_SELECTORS = [
    "[data-role='assistant']",
    "[class*='assistant'][class*='message']",
    "[class*='Assistant']",
    "[class*='message'][class*='assistant']",
    ".markdown-body",
    "[class*='markdown']",
    "[class*='response'][class*='content']",
    "[class*='Message']",
    "article[class*='assistant']",
    "[role='article']",
    "[class*='bubble'][class*='assistant']",
    "[class*='content']",
]

QWEN_REPLY_SELECTORS = [
    "[data-role='assistant']",
    "[class*='assistant'][class*='message']",
    "[class*='answer']",
    "[class*='Answer']",
    "[class*='response']",
    ".markdown-body",
    "[class*='markdown']",
    "[class*='message']",
    "[class*='content']",
    "article",
    "[role='article']",
]

KIMI_REPLY_SELECTORS = [
    "[data-testid='virtuoso-item-list'] [data-role='assistant']",
    "[data-testid='virtuoso-item-list'] [class*='assistant']",
    "[data-testid='virtuoso-item-list'] [class*='message']",
    "[data-testid='virtuoso-item-list'] [class*='content']",
    "[data-testid='virtuoso-item-list'] article",
    "[data-role='assistant']",
    "[class*='message'][class*='assistant']",
    ".markdown-body",
    "[class*='markdown']",
    "[class*='content']",
    "article",
]

# MiniMax (agent.minimaxi.com) often uses agent/chat-style containers; prefer last assistant-style block
MINIMAX_REPLY_SELECTORS = [
    "[data-role='assistant']",
    "[class*='assistant'][class*='message']",
    "[class*='Assistant']",
    "[class*='agent'][class*='message']",
    "[class*='Agent'][class*='content']",
    "[class*='message'][class*='assistant']",
    "[class*='chat'][class*='message']",
    "[class*='Chat'][class*='content']",
    "[class*='reply']",
    "[class*='Reply']",
    "[class*='answer']",
    "[class*='response']",
    "[class*='content'][class*='message']",
    ".markdown-body",
    "[class*='markdown']",
    "[class*='prose']",
    "article",
    "[role='article']",
]


def _reply_text_js_for_platform(platform_id: str) -> str:
    """Platform-specific merge-and-last reply extraction JS (last node with substantial text)."""
    selector_map = {
        "zhipu": ZHIPU_REPLY_SELECTORS,
        "qwen": QWEN_REPLY_SELECTORS,
        "kimi": KIMI_REPLY_SELECTORS,
        "minimax": MINIMAX_REPLY_SELECTORS,
    }
    sels = selector_map.get(platform_id) or (
        ZHIPU_REPLY_SELECTORS + QWEN_REPLY_SELECTORS + KIMI_REPLY_SELECTORS
    )
    return _reply_text_js_merge_and_last(sels)


# MiniMax fallback: get last substantial text block from main/chat area (for varying DOM)
MINIMAX_FALLBACK_JS = """
() => {
    var minLen = 15;
    var roots = document.querySelectorAll('main, [role="main"], [class*="container"], [class*="content"], [class*="chat"], [class*="conversation"]');
    var candidates = [];
    for (var r = 0; r < roots.length; r++) {
        var root = roots[r];
        var nodes = root.querySelectorAll('[class*="message"], [class*="content"], [class*="reply"], [class*="answer"], article, .markdown-body, [class*="markdown"], [class*="prose"]');
        for (var i = 0; i < nodes.length; i++) {
            var el = nodes[i];
            var text = (el.innerText || el.textContent || '').trim();
            if (text.length >= minLen && !el.querySelector('textarea')) candidates.push({ el: el, text: text });
        }
    }
    if (candidates.length === 0) return '';
    candidates.sort(function(a, b) {
        var p = a.el.compareDocumentPosition(b.el);
        if (p & Node.DOCUMENT_POSITION_FOLLOWING) return -1;
        if (p & Node.DOCUMENT_POSITION_PRECEDING) return 1;
        return 0;
    });
    return candidates[candidates.length - 1].text;
}
"""


async def get_latest_reply(page: Any, platform_id: str) -> Dict[str, Any]:
    """Extract latest assistant reply text from the platform tab."""
    try:
        if page.is_closed():
            return {"text": "", "error": "page closed"}
        await asyncio.sleep(0.3)
        js = _reply_text_js_for_platform(platform_id)
        text = await page.evaluate(js)
        text = (text or "").strip()
        # MiniMax: if primary selectors return nothing, try fallback (main/chat area last block)
        if platform_id == "minimax" and len(text) < REPLY_MIN_TEXT_LEN:
            fallback = await page.evaluate(MINIMAX_FALLBACK_JS)
            if fallback and len((fallback or "").strip()) >= REPLY_MIN_TEXT_LEN:
                text = (fallback or "").strip()
        return {"text": text, "error": None}
    except Exception as e:
        return {"text": "", "error": str(e)}


async def check_login_status(platform: Platform) -> Dict[str, Any]:
    """Check if user is logged in to a platform."""
    try:
        await browser_pool.init_playwright()
        browser = await browser_pool.get_browser(platform)
        context = browser_pool.contexts[platform]

        cookies = await load_cookies(platform)
        if cookies:
            await context.add_cookies(cookies)

        page = await context.new_page()
        await page.goto(PLATFORM_URLS[platform.value], wait_until="networkidle")

        is_logged_in = await page.evaluate("""
            () => {
                const indicators = [
                    document.querySelector('[data-testid="user-avatar"]'),
                    document.querySelector('.user-profile'),
                    document.querySelector('[class*="avatar"]'),
                    document.querySelector('[class*="nickname"]')
                ];
                return indicators.some(el => el !== null);
            }
        """)

        await page.close()

        return {
            "platform": platform.value,
            "logged_in": is_logged_in,
            "status": "ok"
        }
    except Exception as e:
        return {
            "platform": platform.value,
            "logged_in": False,
            "status": "error",
            "message": str(e)
        }


async def query_platform(platform: Platform, question: str) -> Dict[str, Any]:
    """Query a single LLM platform (legacy: full flow with wait)."""
    start_time = time.time()

    try:
        await browser_pool.init_playwright()
        browser = await browser_pool.get_browser(platform)
        context = browser_pool.contexts[platform]

        cookies = await load_cookies(platform)
        if cookies:
            await context.add_cookies(cookies)

        page = await context.new_page()

        await page.goto(PLATFORM_URLS[platform.value], wait_until="networkidle")

        if platform == Platform.ZHIPU:
            response = await _query_zhipu(page, question)
        elif platform == Platform.QWEN:
            response = await _query_qwen(page, question)
        elif platform == Platform.KIMI:
            response = await _query_kimi(page, question)
        elif platform == Platform.MINIMAX:
            response = await _query_minimax(page, question)
        else:
            response = {"error": f"Unknown platform: {platform}"}

        await page.close()

        elapsed_time = time.time() - start_time

        return {
            "platform": platform.value,
            "response": response,
            "elapsed_time": elapsed_time,
            "status": "success"
        }

    except Exception as e:
        return {
            "platform": platform.value,
            "response": {"error": str(e)},
            "elapsed_time": time.time() - start_time,
            "status": "error"
        }


async def _query_zhipu(page: Any, question: str) -> Dict[str, Any]:
    """Query 智谱AI (Zhipu AI)."""
    try:
        input_selectors = [
            'textarea[placeholder*="请输入"]',
            'textarea[data-testid="chat-input"]',
            'div[contenteditable="true"]'
        ]
        input_elem = None
        for selector in input_selectors:
            input_elem = await page.query_selector(selector)
            if input_elem:
                break
        if not input_elem:
            return {"error": "Could not find input box"}
        await input_elem.fill(question)
        button_selectors = ['button[type="submit"]', 'button:has-text("发送")', 'button:has-text("提交")']
        send_button = None
        for selector in button_selectors:
            send_button = await page.query_selector(selector)
            if send_button:
                break
        if send_button:
            await send_button.click()
            await page.wait_for_load_state("networkidle", timeout=30000)
            response_text = await page.evaluate("""
                () => {
                    const messages = document.querySelectorAll('[class*="message"]');
                    const lastMessage = messages[messages.length - 1];
                    return lastMessage ? lastMessage.innerText : '';
                }
            """)
            return {"text": response_text}
        return {"error": "Could not find send button"}
    except Exception as e:
        return {"error": str(e)}


async def _query_qwen(page: Any, question: str) -> Dict[str, Any]:
    """Query 千问 (Qwen)."""
    try:
        input_elem = await page.query_selector('textarea[placeholder*="输入"]') or await page.query_selector('div[contenteditable="true"]')
        if not input_elem:
            return {"error": "Could not find input box"}
        await input_elem.fill(question)
        await page.keyboard.press("Enter")
        await page.wait_for_load_state("networkidle", timeout=30000)
        response_text = await page.evaluate("""
            () => {
                const responses = document.querySelectorAll('[class*="response"]');
                const lastResponse = responses[responses.length - 1];
                return lastResponse ? lastResponse.innerText : '';
            }
        """)
        return {"text": response_text}
    except Exception as e:
        return {"error": str(e)}


async def _query_kimi(page: Any, question: str) -> Dict[str, Any]:
    """Query Kimi (Moonshot AI)."""
    try:
        input_selectors = ['textarea[placeholder*="发送"]', 'textarea[placeholder*="输入"]', 'div[contenteditable="true"]']
        input_elem = None
        for selector in input_selectors:
            input_elem = await page.query_selector(selector)
            if input_elem:
                break
        if not input_elem:
            return {"error": "Could not find input box"}
        await input_elem.fill(question)
        await page.keyboard.press("Enter")
        await page.wait_for_load_state("networkidle", timeout=30000)
        response_text = await page.evaluate("""
            () => {
                const messages = document.querySelectorAll('[class*="message"]');
                const lastMessage = messages[messages.length - 1];
                return lastMessage ? lastMessage.innerText : '';
            }
        """)
        return {"text": response_text}
    except Exception as e:
        return {"error": str(e)}


async def _query_minimax(page: Any, question: str) -> Dict[str, Any]:
    """Query MiniMax."""
    try:
        input_selectors = ['textarea[placeholder*="输入"]', 'textarea[placeholder*="问题"]', 'div[contenteditable="true"]']
        input_elem = None
        for selector in input_selectors:
            input_elem = await page.query_selector(selector)
            if input_elem:
                break
        if not input_elem:
            return {"error": "Could not find input box"}
        await input_elem.fill(question)
        await page.keyboard.press("Enter")
        await page.wait_for_load_state("networkidle", timeout=30000)
        response_text = await page.evaluate("""
            () => {
                const messages = document.querySelectorAll('[class*="message"]');
                const lastMessage = messages[messages.length - 1];
                return lastMessage ? lastMessage.innerText : '';
            }
        """)
        return {"text": response_text}
    except Exception as e:
        return {"error": str(e)}


async def analyze_responses(responses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze responses from multiple platforms."""
    analysis = {
        "total_platforms": len(responses),
        "successful": sum(1 for r in responses if r.get("status") == "success"),
        "failed": sum(1 for r in responses if r.get("status") == "error"),
        "platforms": []
    }
    for response in responses:
        platform_analysis = {
            "platform": response.get("platform"),
            "status": response.get("status"),
            "elapsed_time": response.get("elapsed_time", 0),
        }
        if response.get("status") == "success":
            resp_text = response.get("response", {}).get("text", "")
            platform_analysis["response_length"] = len(resp_text)
            platform_analysis["word_count"] = len(resp_text.split())
        else:
            platform_analysis["error"] = response.get("response", {}).get("error", "Unknown error")
        analysis["platforms"].append(platform_analysis)
    return analysis


# ----- Lifespan and MCP (must be defined before custom routes that use mcp) -----
@asynccontextmanager
async def _http_browser_lifespan(app: Any):
    global http_state
    from playwright.async_api import async_playwright

    state = HTTPBrowserState()
    http_state = state
    compare_open_task: Optional[asyncio.Task] = None
    port = getattr(mcp.settings, "port", 8000)
    compare_url_prefix = f"http://localhost:{port}"
    compare_url_prefix_alt = f"http://127.0.0.1:{port}"

    try:
        state.playwright = await async_playwright().start()

        # Try to connect to existing browser (from a previous run that did not close)
        try:
            browser = await state.playwright.chromium.connect_over_cdp(
                f"http://127.0.0.1:{CDP_PORT}"
            )
            contexts = browser.contexts
            if contexts:
                ctx = contexts[0]
                state.browser = browser
                state.context = ctx
                for page in ctx.pages:
                    if page.is_closed():
                        continue
                    url = page.url
                    for pid, base_url in PLATFORM_URLS.items():
                        if url.startswith(base_url) or base_url.rstrip("/") in url:
                            state.pages[pid] = page
                            state.reply_statuses[pid] = "question_sent"
                            break
                    if state.compare_page is None and (
                        url.startswith(compare_url_prefix + "/")
                        or url.startswith(compare_url_prefix_alt + "/")
                        or (str(port) in url and ("localhost" in url or "127.0.0.1" in url))
                    ):
                        state.compare_page = page
                # Open any missing platform tab
                for pid, url in PLATFORM_URLS.items():
                    if pid not in state.pages or state.pages[pid].is_closed():
                        page = await state.context.new_page()
                        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                        state.pages[pid] = page
                        state.reply_statuses[pid] = "question_sent"
                # Open compare tab if missing
                if state.compare_page is None or state.compare_page.is_closed():
                    state.compare_page = await state.context.new_page()

                    async def _open_compare_after_server_up() -> None:
                        async with httpx.AsyncClient() as client:
                            for _ in range(30):
                                await asyncio.sleep(0.5)
                                try:
                                    r = await client.get(
                                        f"http://127.0.0.1:{port}/health",
                                        timeout=2.0,
                                    )
                                    if r.status_code == 200:
                                        break
                                except Exception:
                                    continue
                            else:
                                return
                        try:
                            await state.compare_page.goto(
                                compare_url_prefix + "/",
                                wait_until="domcontentloaded",
                                timeout=15000,
                            )
                        except Exception:
                            pass

                    compare_open_task = asyncio.create_task(_open_compare_after_server_up())
                yield state
                return
            try:
                await browser.close()
            except Exception:
                pass
        except Exception:
            pass

        # No existing browser: launch new one in a detached process so it survives Ctrl+C
        os.makedirs(USER_DATA_DIR, exist_ok=True)
        launched = _launch_browser_detached(USER_DATA_DIR, CDP_PORT)
        if launched:
            for _ in range(30):
                await asyncio.sleep(0.5)
                try:
                    browser = await state.playwright.chromium.connect_over_cdp(
                        f"http://127.0.0.1:{CDP_PORT}"
                    )
                    contexts = browser.contexts
                    if contexts:
                        state.browser = browser
                        state.context = contexts[0]
                        break
                    await browser.close()
                except Exception:
                    continue
            else:
                launched = False
        if not launched:
            # Fallback: launch as child with same USER_DATA_DIR so login state is preserved.
            # Note: browser will close when process exits (e.g. Ctrl+C); use Chrome in
            # /Applications (macOS) or on PATH so detached launch succeeds to keep browser open.
            state.context = await state.playwright.chromium.launch_persistent_context(
                USER_DATA_DIR,
                headless=False,
                args=[f"--remote-debugging-port={CDP_PORT}"],
            )
            state.browser = state.context

        async def open_one_tab(platform_id: str, url: str) -> None:
            page = await state.context.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            state.pages[platform_id] = page
            state.reply_statuses[platform_id] = "question_sent"

        await asyncio.gather(
            *[open_one_tab(pid, url) for pid, url in PLATFORM_URLS.items()]
        )

        state.compare_page = await state.context.new_page()

        async def _open_compare_after_server_up() -> None:
            async with httpx.AsyncClient() as client:
                for _ in range(30):
                    await asyncio.sleep(0.5)
                    try:
                        r = await client.get(
                            f"http://127.0.0.1:{port}/health",
                            timeout=2.0,
                        )
                        if r.status_code == 200:
                            break
                    except Exception:
                        continue
                else:
                    return
            try:
                await state.compare_page.goto(
                    compare_url_prefix + "/",
                    wait_until="domcontentloaded",
                    timeout=15000,
                )
            except Exception:
                pass

        compare_open_task = asyncio.create_task(_open_compare_after_server_up())

        yield state
    finally:
        if compare_open_task is not None and not compare_open_task.done():
            compare_open_task.cancel()
            try:
                await compare_open_task
            except asyncio.CancelledError:
                pass
        # Do not close browser/tabs on exit: keep the four platform pages and comparison page open
        state.pages.clear()
        state.compare_page = None
        state.context = None
        state.browser = None
        # Do not call context.close() or playwright.stop() so the browser window and tabs remain open
        http_state = None


def _get_lifespan(app: Any):
    """Lifespan for HTTP mode: open browser and 5 tabs on startup."""
    return _http_browser_lifespan(app)


mcp = FastMCP("llm_comparison_mcp", lifespan=_get_lifespan)


# ----- Custom HTTP routes (comparison UI and API) -----
def _get_http_state() -> Optional[HTTPBrowserState]:
    return http_state


@mcp.custom_route("/", methods=["GET"], include_in_schema=False)
async def serve_compare_page(request: Request) -> Response:
    """Serve the comparison frontend (index.html)."""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path, media_type="text/html")
    return JSONResponse({"error": "Frontend not found"}, status_code=404)


@mcp.custom_route("/health", methods=["GET"], include_in_schema=False)
async def health_check(request: Request) -> Response:
    """Health check for the server."""
    state = _get_http_state()
    return JSONResponse({
        "status": "ok",
        "browser_ready": state is not None and state.browser is not None,
    })


@mcp.custom_route("/query", methods=["POST"], include_in_schema=False)
async def api_query(request: Request) -> Response:
    """Send question to selected platform tabs."""
    state = _get_http_state()
    if not state or not state.pages:
        return JSONResponse(
            {"ok": False, "error": "Browser or tabs not ready. Start server with HTTP mode (port)."},
            status_code=503,
        )
    try:
        body = await request.json()
        question = (body.get("question") or "").strip()
        platforms = body.get("platforms") or ["zhipu", "qwen", "kimi", "minimax"]
        if not question:
            return JSONResponse({"ok": False, "error": "question is required"}, status_code=400)
    except Exception:
        return JSONResponse({"ok": False, "error": "Invalid JSON body"}, status_code=400)

    async with state._lock:
        state.last_question = question
        for pid in list(state.pages.keys()):
            if pid in platforms:
                state.reply_statuses[pid] = "question_sent"

    errors = []
    for pid in platforms:
        page = state.pages.get(pid)
        if not page or page.is_closed():
            errors.append(f"{pid}: no page")
            continue
        err = await send_question_to_page(pid, page, question)
        if err:
            errors.append(f"{pid}: {err}")
            async with state._lock:
                state.reply_statuses[pid] = "error"

    # Check login status for each requested platform (so UI can prompt user to log in)
    login_status: Dict[str, bool] = {}
    for pid in platforms:
        page = state.pages.get(pid)
        if page and not page.is_closed():
            login_status[pid] = await _check_page_logged_in(page)
        else:
            login_status[pid] = False
    not_logged_in = [pid for pid in platforms if not login_status.get(pid, False)]

    return JSONResponse({
        "ok": True,
        "message": "Question sent to selected platforms.",
        "errors": errors if errors else None,
        "login_status": login_status,
        "not_logged_in": not_logged_in,
    })


@mcp.custom_route("/status", methods=["GET"], include_in_schema=False)
async def api_status(request: Request) -> Response:
    """Return current reply status per platform (for UI polling)."""
    state = _get_http_state()
    if not state:
        return JSONResponse({"platforms": {}, "question": None})
    async with state._lock:
        # Map internal keys to display labels
        display = {}
        for pid, key in state.reply_statuses.items():
            display[pid] = REPLY_STATUS.get(key, key)
        return JSONResponse({
            "platforms": display,
            "question": state.last_question,
        })


@mcp.custom_route("/fetch-replies", methods=["POST"], include_in_schema=False)
async def api_fetch_replies(request: Request) -> Response:
    """Fetch latest reply from each platform tab and return for side-by-side comparison."""
    state = _get_http_state()
    if not state or not state.pages:
        return JSONResponse(
            {"ok": False, "error": "Browser or tabs not ready."},
            status_code=503,
        )
    responses = []
    async with state._lock:
        question = state.last_question
    for pid, page in state.pages.items():
        if not page or page.is_closed():
            responses.append({"platform": pid, "text": "", "status": "error", "error": "page closed"})
            continue
        try:
            result = await get_latest_reply(page, pid)
            status = state.reply_statuses.get(pid, "unknown")
            responses.append({
                "platform": pid,
                "text": result.get("text") or "",
                "status": "error" if result.get("error") else "success",
                "error": result.get("error"),
            })
        except Exception as e:
            responses.append({"platform": pid, "text": "", "status": "error", "error": str(e)})

    return JSONResponse({
        "ok": True,
        "question": question,
        "responses": responses,
    })


@mcp.custom_route("/open-platforms", methods=["POST"], include_in_schema=False)
async def api_open_platforms(request: Request) -> Response:
    """Open new tabs for platforms that are not open or whose tab was closed. Same window."""
    state = _get_http_state()
    if not state or not state.context:
        return JSONResponse(
            {"ok": False, "error": "Browser not ready. Start server with HTTP mode (port)."},
            status_code=503,
        )
    try:
        body = await request.json() if request.headers.get("content-length") else {}
    except Exception:
        body = {}
    want = body.get("platforms") or list(PLATFORM_URLS.keys())

    to_open = []
    async with state._lock:
        for platform_id in want:
            url = PLATFORM_URLS.get(platform_id)
            if not url:
                continue
            page = state.pages.get(platform_id)
            if page and not page.is_closed():
                continue
            to_open.append(platform_id)

    opened = []
    errors = []
    for platform_id in to_open:
        url = PLATFORM_URLS[platform_id]
        try:
            page = await state.context.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            async with state._lock:
                state.pages[platform_id] = page
                state.reply_statuses[platform_id] = "question_sent"
            opened.append(platform_id)
        except Exception as e:
            errors.append(f"{platform_id}: {e}")

    return JSONResponse({
        "ok": True,
        "message": "Opened missing platform tabs.",
        "opened": opened,
        "errors": errors if errors else None,
    })


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else None
    if port:
        mcp.settings.port = port
        # FastMCP 的 streamable_http_app() 只使用 session_manager 的 lifespan，
        # 不会调用我们传入的 lifespan，因此需要包装一层：先执行浏览器 lifespan，再执行 session_manager
        import uvicorn
        from starlette.applications import Starlette

        original_app = mcp.streamable_http_app()

        @asynccontextmanager
        async def combined_lifespan(app: Any):
            async with _http_browser_lifespan(app):
                async with mcp._session_manager.run():
                    yield

        wrapper_app = Starlette(
            debug=mcp.settings.debug,
            routes=[],
            lifespan=combined_lifespan,
        )
        wrapper_app.mount("/", original_app)

        config = uvicorn.Config(
            wrapper_app,
            host=getattr(mcp.settings, "host", "0.0.0.0"),
            port=port,
            log_level=getattr(mcp.settings, "log_level", "info").lower(),
        )
        server = uvicorn.Server(config)
        asyncio.run(server.serve())
    else:
        mcp.run()