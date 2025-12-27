#!/usr/bin/env python3
"""
Story Verification Runner for Affordabot.

This script executes integration tests corresponding to the YAML stories defined in
docs/TESTING/STORIES/. It maps testing stories to their Python implementation
scripts and reports success/failure.

Usage:
    python scripts/verification/story_runner.py [--story STORY_NAME] [--all]

Examples:
    python scripts/verification/story_runner.py --all
    python scripts/verification/story_runner.py --story economic_impact_validity
"""

import argparse
import importlib.util
import sys
import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

# Determine paths relative to this script
SCRIPT_DIR = Path(__file__).parent.resolve()
# Script is in backend/scripts/verification/
# Repo root is script's parent.parent.parent.parent? 
# verify: backend/scripts/verification/story_runner.py -> backend/scripts/verification/ -> backend/scripts/ -> backend/ -> root
# So 3 parents up from dir, or 4 from file.
REPO_ROOT = SCRIPT_DIR.parent.parent.parent

STORIES_DOC_DIR = REPO_ROOT / "docs/TESTING/STORIES"
STORIES_IMPL_DIR = SCRIPT_DIR / "stories"

@dataclass
class StoryExecution:
    name: str
    yaml_path: Path
    impl_path: Path
    success: bool = False
    message: str = ""

def load_yaml_story(story_name: str) -> Optional[dict]:
    """Load the YAML definition for a story."""
    yaml_path = STORIES_DOC_DIR / f"{story_name}.yml"
    if not yaml_path.exists():
        # Try finding it if extension is included or slightly different
        matches = list(STORIES_DOC_DIR.glob(f"{story_name}*.yml"))
        if matches:
            yaml_path = matches[0]
        else:
            return None
            
    try:
        with open(yaml_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading YAML for {story_name}: {e}")
        return None

def find_implementation(story_name: str) -> Optional[Path]:
    """Find the corresponding Python implementation for a story."""
    # Convention: story_name.yml -> verify_story_name.py or just story_name.py
    # We'll look for verify_{story_name}.py first as per plan
    
    # Clean name (remove extension if present)
    clean_name = story_name.replace(".yml", "").replace(".yaml", "")
    
    candidates = [
        STORIES_IMPL_DIR / f"verify_{clean_name}.py",
        STORIES_IMPL_DIR / f"{clean_name}.py"
    ]
    
    for cand in candidates:
        if cand.exists():
            return cand
            
    return None

def execute_story(story_name: str, implementation_path: Path) -> StoryExecution:
    """Execute the Python implementation of a story."""
    print(f"\n{'='*60}")
    print(f"RUNNING STORY: {story_name}")
    print(f"Implementation: {implementation_path}")
    print(f"{'='*60}")
    
    result = StoryExecution(
        name=story_name,
        yaml_path=STORIES_DOC_DIR / f"{story_name}.yml",
        impl_path=implementation_path
    )
    
    try:
        # Import the module dynamically
        spec = importlib.util.spec_from_file_location(f"story_{story_name}", implementation_path)
        if not spec or not spec.loader:
            raise ImportError(f"Could not load spec for {implementation_path}")
            
        module = importlib.util.module_from_spec(spec)
        sys.modules[f"story_{story_name}"] = module
        spec.loader.exec_module(module)
        
        # Check if it has a run() or main() function
        if hasattr(module, "run_story"):
             # Pass the loaded YAML config if run_story accepts arguments
             # For now, assuming run_story() signature is handled by the script itself
             # or it parses its own args. 
             # Simpler approach: Just run the script as __main__ via subprocess?
             # But dynamic import allows sharing state/mocks more easily if needed.
             # Let's try calling run_story()
             
             success, msg = module.run_story()
             result.success = success
             result.message = msg
             
        elif hasattr(module, "main"):
             module.main()
             result.success = True # specific failure should have raised
             result.message = "Completed successfully"
        else:
             # Fallback: if it's a script that runs on import or plain script
             # integration, usually we want a specific entry point.
             result.success = False
             result.message = "No 'run_story()' or 'main()' entry point found."

    except Exception as e:
        import traceback
        traceback.print_exc()
        result.success = False
        result.message = f"Exception: {str(e)}"
        
    status_icon = "✅" if result.success else "❌"
    print(f"\n{status_icon} RESULT: {result.message}")
    return result

def main():
    parser = argparse.ArgumentParser(description="Affordabot Story Verification Runner")
    parser.add_argument("--story", help="Name of the specific story to run (without .yml extension)")
    parser.add_argument("--all", action="store_true", help="Run all implemented stories")
    
    args = parser.parse_args()
    
    # Ensure we are at repo root or can find paths
    if not STORIES_DOC_DIR.exists():
        print(f"Error: Could not find stories directory at {STORIES_DOC_DIR}")
        print("Please run from repository root.")
        sys.exit(1)
        
    stories_to_run = []
    
    if args.story:
        stories_to_run.append(args.story)
    elif args.all:
        # Find all .yml files in doc dir
        for f in STORIES_DOC_DIR.glob("*.yml"):
            stories_to_run.append(f.stem)
    else:
        parser.print_help()
        sys.exit(0)
        
    results = []
    
    print(f"Found {len(stories_to_run)} stories to check...")
    
    for story_name in stories_to_run:
        impl_path = find_implementation(story_name)
        
        if not impl_path:
            if args.story: # Only warn if explicitly requested, otherwise skip unimplemented
                print(f"⚠️  Skipping {story_name}: No implementation found in {STORIES_IMPL_DIR}")
            continue
            
        result = execute_story(story_name, impl_path)
        results.append(result)
        
    # Summary
    print(f"\n\n{'='*60}")
    print("STORY VERIFICATION SUMMARY")
    print(f"{'='*60}")
    
    all_passed = True
    for r in results:
        status = "✅ PASS" if r.success else "❌ FAIL"
        print(f"{status} | {r.name:30} | {r.message}")
        if not r.success:
            all_passed = False
            
    if not results:
        print("No stories executed.")
        
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
