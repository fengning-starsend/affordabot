import base64
from typing import Any, List, Optional
from playwright.async_api import Page

class PlaywrightAdapter:
    """Adapts Playwright Page to llm-common BrowserAdapter protocol."""
    
    def __init__(self, page: Page, base_url: Optional[str] = None):
        self.page = page
        self.base_url = base_url.rstrip("/") if base_url else None
        self._console_errors = []
        self._network_errors = []

    async def navigate(self, path: str) -> None:
        """Navigate to a relative path or absolute URL."""
        target_url = path
        if self.base_url:
            if path.startswith("/"):
                target_url = f"{self.base_url}{path}"
            elif not path.startswith("http"):
                target_url = f"{self.base_url}/{path}"
             
        await self.page.goto(target_url, wait_until="networkidle", timeout=30000)

    async def click(self, target: str) -> None:
        """Click an element by selector or text content."""
        try:
            await self.page.click(target, timeout=2000)
        except Exception:
            await self.page.click(f"text={target}", timeout=5000)

    async def type_text(self, selector: str, text: str) -> None:
        """Type text into an input field."""
        await self.page.fill(selector, text)

    async def screenshot(self) -> str:
        """Capture screenshot and return as base64 string."""
        screenshot_bytes = await self.page.screenshot(full_page=False)
        return base64.b64encode(screenshot_bytes).decode("utf-8")

    async def get_console_errors(self) -> List[str]:
        return self._console_errors

    async def get_network_errors(self) -> List[dict[str, Any]]:
        return self._network_errors

    async def wait_for_selector(self, selector: str, timeout_ms: int = 5000) -> None:
        await self.page.wait_for_selector(selector, timeout=timeout_ms)

    async def get_current_url(self) -> str:
        return self.page.url

    async def close(self) -> None:
        await self.page.close()

    async def get_content(self) -> str:
        return await self.page.content()

    def start_tracing(self):
        self.page.on("console", lambda msg: self._console_errors.append(msg.text) if msg.type == "error" else None)
        self.page.on("requestfailed", lambda req: self._network_errors.append({
            "url": req.url,
            "method": req.method,
            "message": req.failure if req.failure else "Unknown error",
            "status": 0
        }))
        self.page.on("response", lambda res: self._network_errors.append({
            "url": res.url,
            "method": res.request.method,
            "message": f"Status {res.status}",
            "status": res.status
        }) if res.status >= 400 else None)
