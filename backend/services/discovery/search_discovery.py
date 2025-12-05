import os
import re
import asyncio
from typing import List, Optional
# We use AsyncOpenAI directly for the Chat Search workaround
from openai import AsyncOpenAI
from playwright.async_api import async_playwright
# Use LLM Common's WebSearchResult if available in environment, otherwise local definition fallback
# But we verified llm_common is present.
from llm_common.core.models import WebSearchResult

class SearchDiscoveryService:
    """
    Discovery service that uses Z.ai Chat (with Web Search tool) to find content URLs.
    
    Workaround: Since Z.ai Search API returns 429, we use the Chat API (glm-4.5)
    with `web_search` tool enabled. We parse the URLs from citations.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("ZAI_API_KEY")
        # Use Coding Endpoint for Chat as validated
        self.base_url = "https://api.z.ai/api/coding/paas/v4"
        self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
        self.model = "glm-4.5"

    async def find_urls(self, query: str, count: int = 5) -> List[WebSearchResult]:
        """
        Search for content using Z.ai Chat + Web Search Tool.
        Falls back to Playwright if that fails (e.g. Z.ai 429's even on Chat).
        
        Note: Method name 'find_urls' is used by validate_pipeline.
        """
        try:
            results = await self._search_zai_chat(query, count)
            if results:
                print(f"✅ Z.ai Chat Discovery Success: {len(results)} URLs found.")
                return results
            else:
                print("⚠️ Z.ai Chat returned no URLs. Falling back to Playwright...")
        except Exception as e:
            print(f"⚠️ Z.ai Chat Discovery Failed: {e}. Falling back to Playwright...")
        
        # Fallback to Playwright
        return await self._fallback_search_duckduckgo(query, count)

    async def _search_zai_chat(self, query: str, count: int) -> List[WebSearchResult]:
        """Execute search via Z.ai Chat API."""
        tools = [{
            "type": "web_search",
            "web_search": {
                 "enable": True,
                 "search_result": True,
                 "search_query": query
            }
        }]
        
        messages = [{
            "role": "user", 
            "content": f"Please search for: {query}. Provide a list of relevant links and a brief summary for each."
        }]
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=False,
            extra_body={"tools": tools}
        )
        
        content = response.choices[0].message.content
        if not content:
            return []
            
        # Parse URLs from markdown links: [Title](URL)
        results = []
        matches = re.findall(r'\[([^\]]+)\]\((https?://[^\)]+)\)', content)
        
        seen_urls = set()
        for title, url in matches:
            if url in seen_urls:
                continue
            seen_urls.add(url)
            
            # Simple filter for internal z.ai links or unwanted junk?
            # Z.ai citation links are usually clean.
            
            results.append(WebSearchResult(
                title=title,
                url=url,
                content=content # We put full content or construct snippet? 
                # WebSearchResult.content is usually the page content.
                # Here we only have the citation context. 
                # Let's put the chat response context for now or just generic.
            ))
            
        return results[:count]

    async def _fallback_search_duckduckgo(self, query: str, count: int) -> List[WebSearchResult]:
        """Fallback: Scrape DuckDuckGo using Playwright."""
        print(f"🦆 Falling back to DuckDuckGo/Playwright for: {query}")
        results = []
        async with async_playwright() as p:
            # We must handle browser launch failure gracefully
            try:
                browser = await p.chromium.launch(headless=True)
            except Exception as e:
                print(f"❌ Failed to launch browser: {e}")
                return []
                
            try:
                page = await browser.new_page()
                # Go to DDG HTML version (lighter, easier to scrape)
                await page.goto(f"https://html.duckduckgo.com/html/?q={query}", timeout=15000)
                
                # Extract results
                # DDG HTML selectors: .result__body, .result__a, .result__snippet
                elements = await page.query_selector_all(".result__body")
                
                for el in elements[:count]:
                    try:
                        title_el = await el.query_selector(".result__a")
                        snippet_el = await el.query_selector(".result__snippet")
                        
                        if title_el and snippet_el:
                            title = await title_el.inner_text()
                            url = await title_el.get_attribute("href")
                            snippet = await snippet_el.inner_text()
                            
                            if url and not url.startswith("//") and url not in [r.url for r in results]:
                                results.append(WebSearchResult(
                                    title=title,
                                    url=url,
                                    content=snippet,
                                    source="duckduckgo_fallback"
                                ))
                    except Exception:
                        continue
            except Exception as e:
                print(f"❌ Playwright Fallback Failed during scrape: {e}")
            finally:
                await browser.close()
                
        return results

    async def close(self):
        await self.client.close()
