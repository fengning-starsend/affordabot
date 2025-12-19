"""
Enhanced Playwright screenshot capture for Glass Box UI.
Fixes blank screenshot issue by:
1. Waiting for network idle
2. Waiting for specific content elements
3. Adding delay for React hydration
"""
import asyncio
from playwright.async_api import async_playwright
import os
import sys

# Configuration
BASE_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
ARTIFACT_DIR = "/home/fengning/.gemini/antigravity/brain/9112de99-6087-4677-88e8-ddcb9dc376f2"

async def capture_step(page, step_name: str, url: str, wait_for: str = None):
    """Capture a single step with proper waiting."""
    output_path = f"{ARTIFACT_DIR}/step_{step_name}.png"
    
    print(f"📍 Navigating to {url}")
    await page.goto(url, wait_until="networkidle", timeout=30000)
    
    # Wait for React to hydrate
    await asyncio.sleep(2)
    
    # Wait for specific content if provided
    if wait_for:
        try:
            await page.wait_for_selector(wait_for, timeout=10000)
            print(f"   ✅ Found: {wait_for}")
        except Exception as e:
            print(f"   ⚠️ Element not found: {wait_for} ({e})")
    
    # Additional wait for any animations
    await asyncio.sleep(1)
    
    # Take screenshot
    await page.screenshot(path=output_path, full_page=True)
    print(f"   📸 Saved: {output_path}")
    return output_path

async def capture_run_detail(run_id: str):
    """Capture Glass Box run detail page."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-gpu"]
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900},
            device_scale_factor=2  # Retina quality
        )
        page = await context.new_page()
        
        # Capture the runs list first
        runs_path = await capture_step(
            page, 
            "1_runs_list", 
            f"{BASE_URL}/admin/runs",
            wait_for="table, [role='grid'], .run-row, tr"  # Try multiple selectors
        )
        
        # Capture specific run detail
        detail_path = await capture_step(
            page,
            "2_run_detail",
            f"{BASE_URL}/admin/runs/{run_id}",
            wait_for=".timeline, .step-card, .run-detail, [data-run-id]"
        )
        
        await browser.close()
        return runs_path, detail_path

async def capture_all_steps():
    """Capture multiple pages for complete audit."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        context = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await context.new_page()
        
        steps = [
            ("admin_home", f"{BASE_URL}/admin", "main, .dashboard"),
            ("runs_list", f"{BASE_URL}/admin/runs", "table, [role='grid']"),
        ]
        
        for name, url, selector in steps:
            await capture_step(page, name, url, selector)
        
        await browser.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_id = sys.argv[1]
        print(f"🔍 Capturing run: {run_id}")
        asyncio.run(capture_run_detail(run_id))
    else:
        print("🔍 Capturing all admin pages...")
        asyncio.run(capture_all_steps())
