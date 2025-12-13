import asyncio
import os
import sys
from playwright.async_api import async_playwright

async def main():
    print("🚀 Starting Playwright Spike for Municode...")
    # New deep link URL provided by user
    url = "https://library.municode.com/ca/san_jose/codes/code_of_ordinances?nodeId=TIT1GEPR_CH1.01COAD_1.01.010TIRE"
    
    async with async_playwright() as p:
        # Launch browser (headless for speed)
        print("⏳ Launching browser...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            print(f"⏳ Navigating to {url}...")
            # Network idle is better for SPAs that fetch data after load
            await page.goto(url, wait_until="networkidle", timeout=60000)
            
            # Wait for specific content that indicates the SPA has loaded
            # e.g., "Definitions" or an element with class "chunk-content" or similar
            # Based on previous HTML dump, "Municode" title was there, but content wasn't.
            # We hope for some specific text.
            
            print("⏳ Waiting for content to render (selector '.chunk-content' or 'body')...")
            # Wait longer for SPA
            await page.wait_for_timeout(15000) 
            
            # Get full text
            title = await page.title()
            content = await page.content()
            
            # Save HTML for inspection
            with open("debug_municode.html", "w") as f:
                f.write(content)
            print("📸 Saved debug_municode.html")

            print(f"\n✅ Page Title: {title}")
            
            # Extract some sample text to prove it worked
            body_text = await page.inner_text("body")
            
            print("-" * 50)
            print("Preview of Body Text:")
            print(body_text[:1000].replace("\n", " "))
            print("-" * 50)
            
            # Search in raw content too, in case inner_text missed it
            if "Definitions" in content or "10.04" in content:
                print("SUCCESS: Found expected content keyword in HTML.")
            else:
                print("WARNING: 'Definitions' keyword not found in HTML.")

            if "Definitions" in body_text or "10.04" in body_text:
                print("SUCCESS: Found expected content keyword in body text.")
            else:
                print("WARNING: 'Definitions' keyword not found in body text.")

        except Exception as e:
            print(f"\n❌ Playwright Verification Failed: {e}")
            if 'page' in locals():
                content = await page.content()
                print(f"DEBUG: Dump of content length: {len(content)}")
                print(f"DEBUG: Dump snippet: {content[:500]}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
