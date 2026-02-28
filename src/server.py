#!/usr/bin/env python3
"""
MCP Server for LLM Comparison Tool.

This server provides tools to compare responses from multiple LLM platforms:
- 智谱AI (Zhipu AI)
- 千问 (Qwen/Tongyi)
- Kimi (Moonshot AI)
- MiniMax
"""

import asyncio
import json
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field
from mcp.server.fastmcp import FastMCP

# Initialize MCP Server
mcp = FastMCP("llm_comparison_mcp")

# Constants
CHARACTER_LIMIT = 25000
COOKIE_DIR = os.path.expanduser("~/.llm_comparison_cookies")
PLATFORM_URLS = {
    "zhipu": "https://www.zhipuai.cn/",
    "qwen": "https://tongyi.aliyun.com/",
    "kimi": "https://kimi.moonshot.cn/",
    "minimax": "https://platform.minimax.io/",
}


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


# Global state
@dataclass
class BrowserPool:
    """Manages browser instances for each platform."""
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


# Global browser pool
browser_pool = BrowserPool()


# Cookie Management
async def load_cookies(platform: Platform) -> Optional[Dict]:
    """Load cookies for a platform."""
    cookie_file = os.path.join(COOKIE_DIR, f"{platform.value}.json")
    if os.path.exists(cookie_file):
        with open(cookie_file, 'r') as f:
            return json.load(f)
    return None


async def save_cookies(platform: Platform, cookies: List[Dict]) -> None:
    """Save cookies for a platform."""
    os.makedirs(COOKIE_DIR, exist_ok=True)
    cookie_file = os.path.join(COOKIE_DIR, f"{platform.value}.json")
    with open(cookie_file, 'w') as f:
        json.dump(cookies, f)


async def check_login_status(platform: Platform) -> Dict[str, Any]:
    """Check if user is logged in to a platform."""
    try:
        await browser_pool.init_playwright()
        browser = await browser_pool.get_browser(platform)
        context = browser_pool.contexts[platform]

        # Try to load saved cookies
        cookies = await load_cookies(platform)
        if cookies:
            await context.add_cookies(cookies)

        # Open the platform page
        page = await context.new_page()
        await page.goto(PLATFORM_URLS[platform.value], wait_until="networkidle")

        # Check if logged in (this is platform-specific logic)
        # For now, return basic status
        is_logged_in = await page.evaluate("""
            () => {
                // Check for common logged-in indicators
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
    """Query a single LLM platform."""
    start_time = time.time()

    try:
        await browser_pool.init_playwright()
        browser = await browser_pool.get_browser(platform)
        context = browser_pool.contexts[platform]

        # Load cookies if available
        cookies = await load_cookies(platform)
        if cookies:
            await context.add_cookies(cookies)

        page = await context.new_page()

        # Navigate to platform
        await page.goto(PLATFORM_URLS[platform.value], wait_until="networkidle")

        # Platform-specific query logic
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
        # Find and fill the input box
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

        # Find and click send button
        button_selectors = [
            'button[type="submit"]',
            'button:has-text("发送")',
            'button:has-text("提交")'
        ]

        send_button = None
        for selector in button_selectors:
            send_button = await page.query_selector(selector)
            if send_button:
                break

        if send_button:
            await send_button.click()

            # Wait for response
            await page.wait_for_load_state("networkidle", timeout=30000)

            # Get response text
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
        # Similar logic for Qwen
        input_selectors = [
            'textarea[placeholder*="输入"]',
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

        # Press enter to send
        await page.keyboard.press("Enter")

        # Wait for response
        await page.wait_for_load_state("networkidle", timeout=30000)

        # Get response
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
        input_selectors = [
            'textarea[placeholder*="发送"]',
            'textarea[placeholder*="输入"]',
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
        input_selectors = [
            'textarea[placeholder*="输入"]',
            'textarea[placeholder*="问题"]',
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
    # Simple analysis based on response length and status
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


# MCP Tools
@mcp.tool(
    name="llm_compare",
    annotations={
        "title": "Compare LLM Responses",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def llm_compare(params: CompareLLMsInput) -> str:
    """Compare responses from multiple LLM platforms (智谱AI, 千问, Kimi, MiniMax).

    This tool sends the same question to multiple LLM platforms simultaneously
    and returns their responses for comparison. It supports:
    - All four platforms: 智谱AI (zhipu), 千问 (qwen), Kimi (kimi), MiniMax (minimax)
    - Parallel querying for faster results
    - Response format options (markdown or JSON)

    Args:
        params (CompareLLMsInput): Validated input parameters containing:
            - question (str): The question to ask all LLM platforms
            - platforms (Optional[List[Platform]]): List of platforms to query
            - response_format (ResponseFormat): Output format (markdown or JSON)

    Returns:
        str: JSON-formatted comparison results with the following schema:

        Success response:
        {
            "question": str,           # The original question
            "responses": [
                {
                    "platform": str,   # Platform name (zhipu, qwen, kimi, minimax)
                    "response": str,   # The LLM's response text
                    "elapsed_time": float,  # Time taken in seconds
                    "status": str     # "success" or "error"
                }
            ],
            "analysis": {
                "total_platforms": int,
                "successful": int,
                "failed": int,
                "platforms": [...]
            }
        }

        Error response:
        "Error: <error message>"
    """
    try:
        # Determine which platforms to query
        platforms_to_query = params.platforms if params.platforms else list(Platform)

        # Query all platforms in parallel
        tasks = [query_platform(p, params.question) for p in platforms_to_query]
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Process responses
        processed_responses = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                processed_responses.append({
                    "platform": platforms_to_query[i].value,
                    "response": {"error": str(response)},
                    "elapsed_time": 0,
                    "status": "error"
                })
            else:
                processed_responses.append(response)

        # Analyze responses
        analysis = await analyze_responses(processed_responses)

        result = {
            "question": params.question,
            "responses": processed_responses,
            "analysis": analysis
        }

        if params.response_format == ResponseFormat.JSON:
            return json.dumps(result, indent=2, ensure_ascii=False)
        else:
            # Format as markdown
            lines = ["# LLM Response Comparison", ""]
            lines.append(f"**Question:** {params.question}")
            lines.append(f"**Total Platforms:** {analysis['total_platforms']}")
            lines.append(f"**Successful:** {analysis['successful']} | **Failed:** {analysis['failed']}")
            lines.append("")

            for resp in processed_responses:
                platform = resp.get("platform", "unknown")
                status = resp.get("status", "unknown")
                elapsed = resp.get("elapsed_time", 0)

                lines.append(f"## {platform.upper()}")
                lines.append(f"**Status:** {status} | **Time:** {elapsed:.2f}s")
                lines.append("")

                if status == "success":
                    text = resp.get("response", {}).get("text", "")
                    lines.append(text[:2000])  # Truncate long responses
                else:
                    error = resp.get("response", {}).get("error", "Unknown error")
                    lines.append(f"**Error:** {error}")

                lines.append("")
                lines.append("---")
                lines.append("")

            # Add analysis summary
            lines.append("## Analysis Summary")
            lines.append("")
            lines.append("| Platform | Status | Time (s) | Words |")
            lines.append("|----------|--------|----------|-------|")

            for platform_data in analysis.get("platforms", []):
                p = platform_data.get("platform", "unknown")
                s = platform_data.get("status", "unknown")
                t = platform_data.get("elapsed_time", 0)
                w = platform_data.get("word_count", 0)
                lines.append(f"| {p} | {s} | {t:.2f} | {w} |")

            return "\n".join(lines)

    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool(
    name="llm_query_single",
    annotations={
        "title": "Query Single LLM Platform",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def llm_query_single(params: SingleQueryInput) -> str:
    """Query a single LLM platform.

    This tool sends a question to a specific LLM platform and returns its response.
    Use this when you only need to query one platform instead of all of them.

    Args:
        params (SingleQueryInput): Validated input parameters containing:
            - platform (Platform): The platform to query (zhipu, qwen, kimi, minimax)
            - question (str): The question to ask

    Returns:
        str: JSON-formatted response with the following schema:

        Success response:
        {
            "platform": str,
            "response": str,
            "elapsed_time": float,
            "status": "success"
        }

        Error response:
        {
            "platform": str,
            "response": {"error": str},
            "elapsed_time": float,
            "status": "error"
        }
    """
    try:
        result = await query_platform(params.platform, params.question)

        if params.response_format == ResponseFormat.JSON:
            return json.dumps(result, indent=2, ensure_ascii=False)
        else:
            lines = [f"# {params.platform.value.upper()} Response", ""]
            lines.append(f"**Status:** {result.get('status')}")
            lines.append(f"**Time:** {result.get('elapsed_time', 0):.2f}s")
            lines.append("")

            if result.get("status") == "success":
                lines.append(result.get("response", {}).get("text", ""))
            else:
                lines.append(f"**Error:** {result.get('response', {}).get('error', 'Unknown error')}")

            return "\n".join(lines)

    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool(
    name="llm_check_login",
    annotations={
        "title": "Check LLM Platform Login Status",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def llm_check_login(params: LoginStatusInput) -> str:
    """Check login status for LLM platforms.

    This tool checks whether the user is logged in to the specified LLM platforms.
    If cookies are saved, they will be loaded and used. If not logged in,
    the tool will provide instructions for manual login.

    Args:
        params (LoginStatusInput): Validated input parameters containing:
            - platform (Optional[Platform]): Specific platform to check

    Returns:
        str: JSON-formatted status information with the following schema:

        [
            {
                "platform": str,
                "logged_in": bool,
                "status": str,
                "message": str (optional)
            }
        ]
    """
    try:
        platforms_to_check = [params.platform] if params.platform else list(Platform)

        tasks = [check_login_status(p) for p in platforms_to_check]
        results = await asyncio.gather(*tasks)

        return json.dumps(results, indent=2, ensure_ascii=False)

    except Exception as e:
        return f"Error: {str(e)}"


@mcp.tool(
    name="llm_save_session",
    annotations={
        "title": "Save Current Browser Session",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def llm_save_session(platform: str = Field(..., description="Platform to save session for (zhipu, qwen, kimi, minimax)")) -> str:
    """Save the current browser session (cookies) for a platform.

    This tool saves the current browser session cookies to a file,
    so they can be loaded later for automatic login.

    Args:
        platform (str): The platform to save session for

    Returns:
        str: JSON-formatted result with status
    """
    try:
        p = Platform(platform)
        context = browser_pool.contexts.get(p)

        if not context:
            return json.dumps({"status": "error", "message": "No active session for this platform"})

        cookies = await context.cookies()
        await save_cookies(p, cookies)

        return json.dumps({"status": "success", "message": f"Session saved for {platform}"})

    except ValueError:
        return json.dumps({"status": "error", "message": f"Invalid platform: {platform}"})
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})


if __name__ == "__main__":
    import sys
    # Run with optional port for HTTP transport
    port = int(sys.argv[1]) if len(sys.argv) > 1 else None
    if port:
        mcp.run(transport="streamable_http", port=port)
    else:
        mcp.run()
