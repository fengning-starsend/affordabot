from playwright.async_api import async_playwright
import asyncio
import re

async def intercept_config():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Navigating to Municode San Jose...")
        
        # Intercept requests to find API calls
        async def handle_request(route):
            req = route.request
            if "api.municodeweb.com" in req.url:
                print(f"API CALL DETECTED: {req.url}")
            await route.continue_()

        await page.route("**/*", handle_request)
        
        try:
            await page.goto("https://library.municode.com/ca/san_jose/codes/code_of_ordinances", timeout=30000)
            await page.wait_for_load_state("networkidle")
            
            # Also dump local storage/state if possible
            content = await page.content()
            
            # Search again in rendered content
            client_id_match = re.search(r'clientId["\']\s*:\s*["\'](\d+)["\']', content)
            if client_id_match:
                print(f"Found Client ID in Rendered DOM: {client_id_match.group(1)}")
                
        except Exception as e:
            print(f"Error: {e}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(intercept_config())
