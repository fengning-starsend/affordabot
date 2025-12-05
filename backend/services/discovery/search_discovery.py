import asyncio
import os
import aiohttp
from typing import List
from pydantic import BaseModel
from playwright.async_api import async_playwright

class SearchResultItem(BaseModel):
    url: str
    title: str
    snippet: str
    published_date: str | None = None

class SearchDiscoveryService:
    """
    Service to discover content URLs.
    Strategy:
    1. Try Z.ai Web Search (Coding Endpoint) - Best quality for LLMs.
    2. Fallback to Playwright (DuckDuckGo generic scraper) if Z.ai fails (e.g. 429/Quota).
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        # Confirmed via probe that this is the correct endpoint for our keys, even if quota is issue.
        self.zai_endpoint = "https://api.z.ai/api/coding/paas/v4/web_search"
        
    async def find_urls(self, query: str, count: int = 5) -> List[SearchResultItem]:
        """
        Execute search, preferring Z.ai but falling back on error.
        """
        results = await self._search_zai(query, count)
        if results:
            return results
            
        print(f"⚠️ Falling back to Playwright Discovery (DuckDuckGo) for '{query}'...")
        return await self._search_playwright_ddg(query, count)

    async def _search_zai(self, query: str, count: int) -> List[SearchResultItem]:
        print(f"🔎 Z.ai Discovery (search-prime): '{query}'...")
        async with aiohttp.ClientSession() as session:
            try:
                payload = {
                    "search_engine": "search-prime",
                    "search_query": query,
                    "count": count
                }
                
                async with session.post(
                    self.zai_endpoint, 
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload
                ) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        print(f"⚠️ Z.ai Search Failed ({resp.status}): {error_text[:100]}...")
                        return []
                        
                    data = await resp.json()
                    results = []
                    for item in data.get("search_result", []):
                        results.append(SearchResultItem(
                            url=item.get("link", ""),
                            title=item.get("title", ""),
                            snippet=item.get("content", ""), 
                            published_date=item.get("publish_date")
                        ))
                    return results
            except Exception as e:
                print(f"⚠️ Z.ai Search Exception: {e}")
                return []

    async def _search_playwright_ddg(self, query: str, count: int) -> List[SearchResultItem]:
        print(f"🔎 Playwright Discovery (DDG): '{query}'...")
        results = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            try:
                page = await browser.new_page(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                
                encoded_query = query.replace(" ", "+")
                url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
                
                await page.goto(url, wait_until="networkidle", timeout=15000)
                
                elements = await page.query_selector_all(".result")
                for el in elements[:count]:
                    try:
                        title_el = await el.query_selector(".result__a")
                        snippet_el = await el.query_selector(".result__snippet")
                        
                        if not title_el: continue
                            
                        # Extract info
                        title = await title_el.inner_text()
                        link = await title_el.get_attribute("href")
                        snippet = await snippet_el.inner_text() if snippet_el else ""
                        
                        if link:
                            results.append(SearchResultItem(url=link, title=title, snippet=snippet))
                    except Exception:
                        continue
                        
                return results
                
            except Exception as e:
                print(f"❌ Playwright Discovery Failed: {e}")
                return []
            finally:
                await browser.close()
    
    async def close(self):
        pass
