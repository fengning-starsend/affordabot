#!/usr/bin/env python3
"""
Visual Story Runner - Executes YAML-based visual verification stories using UISmokeAgent.
"""
import argparse
import asyncio
import os
import sys
import yaml
from pathlib import Path

from playwright.async_api import async_playwright

# Add backend root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from scripts.verification.patch_zai import apply_patch
apply_patch()

from scripts.verification.browser_adapter import PlaywrightAdapter
from llm_common.agents import UISmokeAgent
from llm_common.core import LLMConfig
from llm_common.providers import ZaiClient
from llm_common.agents.schemas import AgentStory

async def run_story_file(story_path: Path, base_url: str, output_dir: Path, api_key: str):
    """Run a single story file."""
    print(f"📖 Loading story from {story_path}")
    with open(story_path, "r") as f:
        data = yaml.safe_load(f)
        
    # Convert YAML data to AgentStory schema
    # YAML structure assumption:
    # name: ...
    # persona: ...
    # start_url: ...
    # steps:
    #   - name: ...
    #     action: ...
    #     verification: ...
    
    # We map this to AgentStory steps
    steps = []
    
    # Handle optional start_url (can be an implicit first navigation step or just handled by agent)
    start_url = data.get("start_url", "/admin")
    
    # Add initial navigation as explicit step if not in steps?
    # Logic: UISmokeAgent doesn't auto-navigate to start_url unless it's a step.
    # Let's verify `data['steps']` structure.
    raw_steps = data.get("steps", [])
    
    for idx, raw_step in enumerate(raw_steps):
        # Construct a description that guides the agent
        action = raw_step.get("action", "")
        verification = raw_step.get("verification", "")
        step_id = raw_step.get("name", f"step_{idx+1}").replace(" ", "_").lower()
        
        desc = f"Goal: {action}. Verification required: {verification}."
        if idx == 0 and start_url:
             desc = f"Navigate to {start_url}. " + desc
             
        steps.append({
            "id": step_id,
            "description": desc,
            "validation_criteria": raw_step.get("validation_criteria", []) # Should be list of strings
        })

    story = AgentStory(
        id=data.get("name", story_path.stem).replace(" ", "_"),
        persona=data.get("persona", "User"),
        steps=steps,
        metadata=data
    )
    
    # Run
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Auth attempt (Bypass Header)
        await page.set_extra_http_headers({"x-test-user": "admin"})
        
        adapter = PlaywrightAdapter(page, base_url=base_url)
        adapter.start_tracing()
        
        config = LLMConfig(api_key=api_key, provider="zai", default_model="glm-4.6v")
        llm = ZaiClient(config)
        
        agent = UISmokeAgent(
            glm_client=llm,
            browser=adapter,
            base_url=base_url,
            evidence_dir=str(output_dir)
        )
        
        print(f"▶️ Running Story: {story.id}")
        result = await agent.run_story(story)
        
        # Report
        print(f"🏁 Result: {result.status.upper()}")
        if result.status != "pass":
            print("❌ Story Failed. Check artifacts.")
            return False
        return True

async def main():
    parser = argparse.ArgumentParser(description="Run Visual Stories")
    parser.add_argument("--story", required=False, help="Path to specific YAML story")
    parser.add_argument("--all", action="store_true", help="Run all stories in docs/TESTING/STORIES")
    parser.add_argument("--url", default=os.environ.get("FRONTEND_URL", "http://localhost:3000"))
    parser.add_argument("--output", default="artifacts/verification/stories")
    args = parser.parse_args()
    
    api_key = os.environ.get("ZAI_API_KEY")
    if not api_key:
        print("❌ ZAI_API_KEY required")
        sys.exit(1)
        
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)

    stories_to_run = []
    if args.story:
        stories_to_run.append(Path(args.story))
	    elif args.all:
        # Find all stories in docs/TESTING/STORIES that seem like visual ones?
        # Or just run all and let them succeed?
        # The "Deep Validity" stories are logic based. They might fail if run visually?
        # Actually, `story_runner.py` runs Python scripts (Logic). `visual_story_runner.py` runs YAMLs (Visual).
        # We need to distinguish them.
        # The 4 new stories are YAMLs. The Deep Validity ones ALSO have YAMLs but logic python scripts.
        # This script runs YAML content visually.
        # For now, let's target the 4 specific ones via glob or names found in docs.
	        docs_root = Path(__file__).parent.parent.parent.parent / "docs" / "TESTING" / "STORIES"
	        if docs_root.exists():
	            for f in docs_root.glob("*.yml"):
                # Filter out Deep Validity ones if they are not meant for visual runner?
                # Actually, if we run them visually, they might pass too if the UI supports the flow!
                # But let's verify just the 4 new ones for this task if possible, OR just run them all.
                # Let's run all .yml files found.
                stories_to_run.append(f)
    
    if not stories_to_run:
        print("No stories found.")
        sys.exit(0)
        
    success = True
    for story in stories_to_run:
        if not await run_story_file(story, args.url, output_path, api_key):
            success = False
            
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
