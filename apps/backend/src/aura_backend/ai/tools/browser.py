"""
Production-grade Browser Tool using Playwright.
"""

import asyncio
from typing import Any, Dict, Optional, List
from datetime import datetime

try:
    from playwright.async_api import async_playwright, Browser, Page, BrowserContext
except ImportError:
    async_playwright = None
    Browser = None
    Page = None
    BrowserContext = None

from aura_backend.ai.tools.models import ToolResult, ToolArtifact
from aura_backend.ai.tools.security import URLValidator, create_default_url_policy


class BrowserTool:
    """Production-grade web browsing with Playwright"""

    def __init__(
        self,
        headless: bool = True,
        timeout_seconds: int = 30,
        url_validator: Optional[URLValidator] = None,
    ):
        if async_playwright is None:
            raise ImportError("playwright not installed. Install with: pip install playwright")

        self.headless = headless
        self.timeout_seconds = timeout_seconds
        self.url_validator = url_validator or URLValidator(create_default_url_policy())
        self._playwright_instance = None  # CRITICAL FIX: Store playwright instance
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._pages: Dict[str, Page] = {}
        self._id = "BrowserTool"
        self._created_at = datetime.utcnow()
        self._execution_count = 0
        self._total_execution_time_ms = 0.0

    @property
    def id(self) -> str:
        return self._id

    def get_name(self) -> str:
        return "Browser"

    def get_description(self) -> str:
        return "Web browsing and automation with Playwright"

    def get_capabilities(self):
        """Get available capabilities"""
        from aura_backend.ai.tools import ToolCapability

        return [
            ToolCapability("launch", "Launch browser instance"),
            ToolCapability("close", "Close browser"),
            ToolCapability("navigate", "Navigate to URL"),
            ToolCapability("back", "Go back in history"),
            ToolCapability("forward", "Go forward in history"),
            ToolCapability("reload", "Reload page"),
            ToolCapability("click", "Click element"),
            ToolCapability("double-click", "Double-click element"),
            ToolCapability("hover", "Hover over element"),
            ToolCapability("fill", "Fill form field"),
            ToolCapability("type", "Type text"),
            ToolCapability("press", "Press key"),
            ToolCapability("select", "Select option"),
            ToolCapability("check", "Check checkbox"),
            ToolCapability("uncheck", "Uncheck checkbox"),
            ToolCapability("wait", "Wait for time"),
            ToolCapability("wait-for-selector", "Wait for selector"),
            ToolCapability("extract-text", "Extract text content"),
            ToolCapability("extract-html", "Extract HTML"),
            ToolCapability("extract-links", "Extract links"),
            ToolCapability("screenshot", "Take screenshot"),
            ToolCapability("pdf", "Generate PDF"),
            ToolCapability("get-cookies", "Get cookies"),
            ToolCapability("set-cookies", "Set cookies"),
            ToolCapability("get-local-storage", "Get localStorage"),
            ToolCapability("get-session-storage", "Get sessionStorage"),
        ]

    def get_parameters(self):
        """Get operation parameters"""
        from aura_backend.ai.tools import ToolParameter

        return [
            ToolParameter("operation", "string", "Operation to perform", required=True),
            ToolParameter("url", "string", "URL to navigate to", required=False),
            ToolParameter("selector", "string", "CSS selector", required=False),
            ToolParameter("text", "string", "Text content", required=False),
            ToolParameter("key", "string", "Key to press", required=False),
            ToolParameter("value", "string", "Value to set", required=False),
            ToolParameter("timeout", "integer", "Operation timeout in ms", required=False),
            ToolParameter("page_id", "string", "Page identifier", required=False),
        ]

    async def validate(self, **kwargs) -> Dict[str, Any]:
        """Validate parameters"""
        operation = kwargs.get("operation")

        if not operation:
            return {"valid": False, "error": "operation is required"}

        if operation == "navigate":
            if not kwargs.get("url"):
                return {"valid": False, "error": "url is required"}

        if operation in ["click", "double-click", "hover", "wait-for-selector"]:
            if not kwargs.get("selector"):
                return {"valid": False, "error": "selector is required"}

        return {"valid": True}

    async def execute(self, **kwargs) -> ToolResult:
        """Execute browser operation"""
        start_time = datetime.utcnow()
        result = ToolResult(success=True)

        try:
            operation = kwargs.get("operation")

            if operation == "launch":
                result = await self._launch(result)
            elif operation == "close":
                result = await self._close(result)
            elif operation == "navigate":
                result = await self._navigate(kwargs.get("url"), kwargs.get("page_id"), result)
            elif operation == "back":
                result = await self._go_back(kwargs.get("page_id"), result)
            elif operation == "forward":
                result = await self._go_forward(kwargs.get("page_id"), result)
            elif operation == "reload":
                result = await self._reload(kwargs.get("page_id"), result)
            elif operation == "click":
                result = await self._click(kwargs.get("selector"), kwargs.get("page_id"), result)
            elif operation == "double-click":
                result = await self._double_click(kwargs.get("selector"), kwargs.get("page_id"), result)
            elif operation == "hover":
                result = await self._hover(kwargs.get("selector"), kwargs.get("page_id"), result)
            elif operation == "fill":
                result = await self._fill(kwargs.get("selector"), kwargs.get("text"), kwargs.get("page_id"), result)
            elif operation == "type":
                result = await self._type(kwargs.get("selector"), kwargs.get("text"), kwargs.get("page_id"), result)
            elif operation == "press":
                result = await self._press(kwargs.get("key"), kwargs.get("page_id"), result)
            elif operation == "select":
                result = await self._select(kwargs.get("selector"), kwargs.get("value"), kwargs.get("page_id"), result)
            elif operation == "check":
                result = await self._check(kwargs.get("selector"), kwargs.get("page_id"), result)
            elif operation == "uncheck":
                result = await self._uncheck(kwargs.get("selector"), kwargs.get("page_id"), result)
            elif operation == "wait":
                result = await self._wait(kwargs.get("timeout", 1000), result)
            elif operation == "wait-for-selector":
                result = await self._wait_for_selector(kwargs.get("selector"), kwargs.get("page_id"), result)
            elif operation == "extract-text":
                result = await self._extract_text(kwargs.get("page_id"), result)
            elif operation == "extract-html":
                result = await self._extract_html(kwargs.get("selector"), kwargs.get("page_id"), result)
            elif operation == "extract-links":
                result = await self._extract_links(kwargs.get("page_id"), result)
            elif operation == "screenshot":
                result = await self._screenshot(kwargs.get("page_id"), result)
            elif operation == "pdf":
                result = await self._pdf(kwargs.get("page_id"), result)
            elif operation == "get-cookies":
                result = await self._get_cookies(kwargs.get("page_id"), result)
            elif operation == "get-local-storage":
                result = await self._get_local_storage(kwargs.get("page_id"), result)
            elif operation == "get-session-storage":
                result = await self._get_session_storage(kwargs.get("page_id"), result)
            else:
                result.success = False
                result.add_error(f"Unknown operation: {operation}")

        except Exception as e:
            result.success = False
            result.add_error(str(e))
            result.add_log("ERROR", f"Browser operation failed: {e}")

        duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        result.duration = duration_ms
        self._execution_count += 1
        self._total_execution_time_ms += duration_ms

        return result

    async def _launch(self, result: ToolResult) -> ToolResult:
        """Launch browser"""
        if self._browser is not None:
            result.add_warning("Browser already launched")
            return result

        try:
            # CRITICAL FIX: Store playwright instance to keep it alive
            self._playwright_instance = await async_playwright().start()
            self._browser = await self._playwright_instance.chromium.launch(headless=self.headless)
            self._context = await self._browser.new_context()
            result.data = {"status": "launched", "headless": self.headless}
            result.add_log("INFO", "Browser launched")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to launch browser: {e}")
            # Clean up on failure
            try:
                if self._playwright_instance:
                    await self._playwright_instance.stop()
            except Exception:
                pass
            self._browser = None
            self._context = None
            self._playwright_instance = None

        return result

    async def _close(self, result: ToolResult) -> ToolResult:
        """Close browser"""
        try:
            # Close all pages first
            for page in list(self._pages.values()):
                try:
                    await page.close()
                except Exception:
                    pass
            self._pages.clear()

            # Close context
            if self._context:
                try:
                    await self._context.close()
                except Exception:
                    pass
                self._context = None

            # Close browser
            if self._browser:
                try:
                    await self._browser.close()
                except Exception:
                    pass
                self._browser = None

            # CRITICAL FIX: Close playwright instance
            if self._playwright_instance:
                try:
                    await self._playwright_instance.stop()
                except Exception:
                    pass
                self._playwright_instance = None

            result.data = {"status": "closed"}
            result.add_log("INFO", "Browser closed")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to close browser: {e}")

        return result

    def _get_page(self, page_id: Optional[str]) -> Optional[Page]:
        """Get page by ID or return first/last page"""
        if page_id:
            return self._pages.get(page_id)
        return next(iter(self._pages.values())) if self._pages else None

    def _validate_selector(self, selector: str) -> str:
        """
        Validate CSS selector format.

        Ensures selector is valid CSS, not XPath or other expression language.
        """
        if not selector:
            raise ValueError("Selector is empty")

        if len(selector) > 1024:
            raise ValueError("Selector too long")

        # Block XPath patterns
        if selector.startswith("//") or selector.startswith("("):
            raise ValueError("XPath expressions not allowed")

        # Block JavaScript patterns
        if selector.startswith("javascript:"):
            raise ValueError("JavaScript patterns not allowed")

        # Allow basic CSS selectors
        # This is not exhaustive but catches common abuse patterns
        return selector

    async def _navigate(self, url: str, page_id: Optional[str], result: ToolResult) -> ToolResult:
        """Navigate to URL"""
        if not self._browser:
            result.success = False
            result.add_error("Browser not launched. Call 'launch' first")
            return result

        # CRITICAL FIX: Validate URL against security policy
        try:
            validated_url = self.url_validator.validate_url(url)
        except (ValueError, PermissionError) as e:
            result.success = False
            result.add_error(f"URL validation failed: {str(e)}")
            return result

        try:
            page = self._get_page(page_id)
            if not page:
                page = await self._context.new_page()
                page_id = f"page_{len(self._pages)}"
                self._pages[page_id] = page

            await asyncio.wait_for(page.goto(validated_url), timeout=self.timeout_seconds)
            result.data = {
                "url": page.url,
                "title": await page.title(),
                "page_id": page_id,
            }
            result.add_log("INFO", f"Navigated to {url}")
        except asyncio.TimeoutError:
            result.success = False
            result.add_error(f"Navigation timeout after {self.timeout_seconds} seconds")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to navigate: {e}")

        return result

    async def _go_back(self, page_id: Optional[str], result: ToolResult) -> ToolResult:
        """Go back in history"""
        page = self._get_page(page_id)
        if not page:
            result.success = False
            result.add_error("No page available")
            return result

        try:
            await asyncio.wait_for(page.go_back(), timeout=self.timeout_seconds)
            result.data = {"url": page.url}
            result.add_log("INFO", "Navigated back")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to go back: {e}")

        return result

    async def _go_forward(self, page_id: Optional[str], result: ToolResult) -> ToolResult:
        """Go forward in history"""
        page = self._get_page(page_id)
        if not page:
            result.success = False
            result.add_error("No page available")
            return result

        try:
            await asyncio.wait_for(page.go_forward(), timeout=self.timeout_seconds)
            result.data = {"url": page.url}
            result.add_log("INFO", "Navigated forward")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to go forward: {e}")

        return result

    async def _reload(self, page_id: Optional[str], result: ToolResult) -> ToolResult:
        """Reload page"""
        page = self._get_page(page_id)
        if not page:
            result.success = False
            result.add_error("No page available")
            return result

        try:
            await asyncio.wait_for(page.reload(), timeout=self.timeout_seconds)
            result.data = {"url": page.url}
            result.add_log("INFO", "Page reloaded")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to reload: {e}")

        return result

    async def _click(self, selector: str, page_id: Optional[str], result: ToolResult) -> ToolResult:
        """Click element"""
        page = self._get_page(page_id)
        if not page:
            result.success = False
            result.add_error("No page available")
            return result

        # Validate selector
        try:
            validated_selector = self._validate_selector(selector)
        except ValueError as e:
            result.success = False
            result.add_error(f"Invalid selector: {str(e)}")
            return result

        try:
            await asyncio.wait_for(page.click(validated_selector), timeout=self.timeout_seconds)
            result.data = {"selector": selector}
            result.add_log("INFO", f"Clicked {selector}")
        except asyncio.TimeoutError:
            result.success = False
            result.add_error(f"Click timeout after {self.timeout_seconds} seconds")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to click: {e}")

        return result

    async def _double_click(self, selector: str, page_id: Optional[str], result: ToolResult) -> ToolResult:
        """Double-click element"""
        page = self._get_page(page_id)
        if not page:
            result.success = False
            result.add_error("No page available")
            return result

        try:
            await asyncio.wait_for(page.dblclick(selector), timeout=self.timeout_seconds)
            result.data = {"selector": selector}
            result.add_log("INFO", f"Double-clicked {selector}")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to double-click: {e}")

        return result

    async def _hover(self, selector: str, page_id: Optional[str], result: ToolResult) -> ToolResult:
        """Hover over element"""
        page = self._get_page(page_id)
        if not page:
            result.success = False
            result.add_error("No page available")
            return result

        try:
            await asyncio.wait_for(page.hover(selector), timeout=self.timeout_seconds)
            result.data = {"selector": selector}
            result.add_log("INFO", f"Hovered over {selector}")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to hover: {e}")

        return result

    async def _fill(self, selector: str, text: str, page_id: Optional[str], result: ToolResult) -> ToolResult:
        """Fill form field"""
        page = self._get_page(page_id)
        if not page:
            result.success = False
            result.add_error("No page available")
            return result

        try:
            await asyncio.wait_for(page.fill(selector, str(text)), timeout=self.timeout_seconds)
            result.data = {"selector": selector, "text_length": len(str(text))}
            result.add_log("INFO", f"Filled {selector}")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to fill: {e}")

        return result

    async def _type(self, selector: str, text: str, page_id: Optional[str], result: ToolResult) -> ToolResult:
        """Type text"""
        page = self._get_page(page_id)
        if not page:
            result.success = False
            result.add_error("No page available")
            return result

        try:
            await asyncio.wait_for(page.type(selector, str(text)), timeout=self.timeout_seconds)
            result.data = {"selector": selector, "text_length": len(str(text))}
            result.add_log("INFO", f"Typed in {selector}")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to type: {e}")

        return result

    async def _press(self, key: str, page_id: Optional[str], result: ToolResult) -> ToolResult:
        """Press key"""
        page = self._get_page(page_id)
        if not page:
            result.success = False
            result.add_error("No page available")
            return result

        try:
            await asyncio.wait_for(page.press("body", key), timeout=self.timeout_seconds)
            result.data = {"key": key}
            result.add_log("INFO", f"Pressed key: {key}")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to press key: {e}")

        return result

    async def _select(self, selector: str, value: str, page_id: Optional[str], result: ToolResult) -> ToolResult:
        """Select option"""
        page = self._get_page(page_id)
        if not page:
            result.success = False
            result.add_error("No page available")
            return result

        try:
            await asyncio.wait_for(page.select_option(selector, str(value)), timeout=self.timeout_seconds)
            result.data = {"selector": selector, "value": value}
            result.add_log("INFO", f"Selected {value}")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to select: {e}")

        return result

    async def _check(self, selector: str, page_id: Optional[str], result: ToolResult) -> ToolResult:
        """Check checkbox"""
        page = self._get_page(page_id)
        if not page:
            result.success = False
            result.add_error("No page available")
            return result

        try:
            await asyncio.wait_for(page.check(selector), timeout=self.timeout_seconds)
            result.data = {"selector": selector}
            result.add_log("INFO", f"Checked {selector}")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to check: {e}")

        return result

    async def _uncheck(self, selector: str, page_id: Optional[str], result: ToolResult) -> ToolResult:
        """Uncheck checkbox"""
        page = self._get_page(page_id)
        if not page:
            result.success = False
            result.add_error("No page available")
            return result

        try:
            await asyncio.wait_for(page.uncheck(selector), timeout=self.timeout_seconds)
            result.data = {"selector": selector}
            result.add_log("INFO", f"Unchecked {selector}")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to uncheck: {e}")

        return result

    async def _wait(self, timeout_ms: int, result: ToolResult) -> ToolResult:
        """Wait for time"""
        try:
            await asyncio.sleep(timeout_ms / 1000)
            result.data = {"waited_ms": timeout_ms}
            result.add_log("INFO", f"Waited {timeout_ms}ms")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to wait: {e}")

        return result

    async def _wait_for_selector(self, selector: str, page_id: Optional[str], result: ToolResult) -> ToolResult:
        """Wait for selector"""
        page = self._get_page(page_id)
        if not page:
            result.success = False
            result.add_error("No page available")
            return result

        try:
            await asyncio.wait_for(page.wait_for_selector(selector), timeout=self.timeout_seconds)
            result.data = {"selector": selector}
            result.add_log("INFO", f"Selector appeared: {selector}")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to wait for selector: {e}")

        return result

    async def _extract_text(self, page_id: Optional[str], result: ToolResult) -> ToolResult:
        """Extract text content"""
        page = self._get_page(page_id)
        if not page:
            result.success = False
            result.add_error("No page available")
            return result

        try:
            text = await asyncio.wait_for(page.evaluate("document.body.innerText"), timeout=self.timeout_seconds)
            result.data = {"text": text, "length": len(text)}
            result.add_log("INFO", f"Extracted {len(text)} characters")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to extract text: {e}")

        return result

    async def _extract_html(self, selector: Optional[str], page_id: Optional[str], result: ToolResult) -> ToolResult:
        """Extract HTML"""
        page = self._get_page(page_id)
        if not page:
            result.success = False
            result.add_error("No page available")
            return result

        try:
            if selector:
                html = await asyncio.wait_for(
                    page.evaluate(f"document.querySelector('{selector}').outerHTML"),
                    timeout=self.timeout_seconds
                )
            else:
                html = await asyncio.wait_for(page.evaluate("document.body.outerHTML"), timeout=self.timeout_seconds)

            result.data = {"html": html, "length": len(html)}
            result.add_log("INFO", f"Extracted {len(html)} characters of HTML")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to extract HTML: {e}")

        return result

    async def _extract_links(self, page_id: Optional[str], result: ToolResult) -> ToolResult:
        """Extract links"""
        page = self._get_page(page_id)
        if not page:
            result.success = False
            result.add_error("No page available")
            return result

        try:
            links = await asyncio.wait_for(
                page.evaluate("""
                    Array.from(document.querySelectorAll('a'))
                        .map(a => ({href: a.href, text: a.innerText}))
                """),
                timeout=self.timeout_seconds
            )
            result.data = {"links": links, "count": len(links)}
            result.add_log("INFO", f"Extracted {len(links)} links")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to extract links: {e}")

        return result

    async def _screenshot(self, page_id: Optional[str], result: ToolResult) -> ToolResult:
        """Take screenshot"""
        page = self._get_page(page_id)
        if not page:
            result.success = False
            result.add_error("No page available")
            return result

        try:
            screenshot = await asyncio.wait_for(page.screenshot(), timeout=self.timeout_seconds)
            result.data = {"screenshot_bytes": len(screenshot), "format": "png"}
            result.add_log("INFO", f"Screenshot taken ({len(screenshot)} bytes)")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to take screenshot: {e}")

        return result

    async def _pdf(self, page_id: Optional[str], result: ToolResult) -> ToolResult:
        """Generate PDF"""
        page = self._get_page(page_id)
        if not page:
            result.success = False
            result.add_error("No page available")
            return result

        try:
            pdf = await asyncio.wait_for(page.pdf(), timeout=self.timeout_seconds)
            result.data = {"pdf_bytes": len(pdf), "format": "pdf"}
            result.add_log("INFO", f"PDF generated ({len(pdf)} bytes)")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to generate PDF: {e}")

        return result

    async def _get_cookies(self, page_id: Optional[str], result: ToolResult) -> ToolResult:
        """Get cookies"""
        if not self._context:
            result.success = False
            result.add_error("No browser context")
            return result

        try:
            cookies = await self._context.cookies()
            result.data = {"cookies": cookies, "count": len(cookies)}
            result.add_log("INFO", f"Retrieved {len(cookies)} cookies")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to get cookies: {e}")

        return result

    async def _get_local_storage(self, page_id: Optional[str], result: ToolResult) -> ToolResult:
        """Get localStorage"""
        page = self._get_page(page_id)
        if not page:
            result.success = False
            result.add_error("No page available")
            return result

        try:
            storage = await asyncio.wait_for(
                page.evaluate("JSON.stringify(localStorage)"),
                timeout=self.timeout_seconds
            )
            result.data = {"storage": storage}
            result.add_log("INFO", "Retrieved localStorage")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to get localStorage: {e}")

        return result

    async def _get_session_storage(self, page_id: Optional[str], result: ToolResult) -> ToolResult:
        """Get sessionStorage"""
        page = self._get_page(page_id)
        if not page:
            result.success = False
            result.add_error("No page available")
            return result

        try:
            storage = await asyncio.wait_for(
                page.evaluate("JSON.stringify(sessionStorage)"),
                timeout=self.timeout_seconds
            )
            result.data = {"storage": storage}
            result.add_log("INFO", "Retrieved sessionStorage")
        except Exception as e:
            result.success = False
            result.add_error(f"Failed to get sessionStorage: {e}")

        return result

    async def health(self) -> Dict[str, Any]:
        """Get tool health status"""
        return {
            "status": "healthy" if self._browser else "ready",
            "browser_launched": self._browser is not None,
            "pages_open": len(self._pages),
            "execution_count": self._execution_count,
            "total_time_ms": self._total_execution_time_ms,
        }

    @property
    def timeout_seconds(self) -> float:
        return self.timeout_seconds

    async def get_info(self) -> Dict[str, Any]:
        """Get complete tool information"""
        return {
            "id": self.id,
            "name": self.get_name(),
            "description": self.get_description(),
            "capabilities": [
                {
                    "name": cap.name,
                    "description": cap.description,
                    "version": cap.version,
                }
                for cap in self.get_capabilities()
            ],
            "parameters": [
                {
                    "name": param.name,
                    "type": param.type,
                    "description": param.description,
                    "required": param.required,
                }
                for param in self.get_parameters()
            ],
            "timeout_seconds": self.timeout_seconds,
            "execution_count": self._execution_count,
            "total_execution_time_ms": self._total_execution_time_ms,
        }
