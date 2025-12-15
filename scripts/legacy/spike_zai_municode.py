import asyncio
import os
import sys
from pydantic import BaseModel, Field
from typing import List, Optional

# Add backend to path so imports work
# We assume this script is run from project root or scripts/ dir
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from backend.services.extractors.zai import ZaiExtractor

# --- Schema for Municode ---
class CodeSection(BaseModel):
    section_id: str = Field(..., description="The section identifier, e.g., '10.04.010'")
    title: str = Field(..., description="Title of the section")
    content: str = Field(..., description="The full text content of the section")

class MunicodePage(BaseModel):
    title: str = Field(..., description="Page title")
    chapter_id: Optional[str] = Field(None, description="Chapter identifier if present")
    sections: List[CodeSection] = Field(..., description="List of code sections found on the page")

# --- Spike ---

async def main():
    api_key = os.environ.get("ZAI_API_KEY")
    if not api_key:
        print("❌ ZAI_API_KEY not found in environment.")
        return

    # Sample URL from San Jose Municode (New Deep Link)
    url = "https://library.municode.com/ca/san_jose/codes/code_of_ordinances?nodeId=TIT1GEPR_CH1.01COAD_1.01.010TIRE" 
    
    print(f"🚀 Starting Z.ai Spike for URL: {url}")
    print(f"key: {api_key[:5]}...")

    extractor = ZaiExtractor(api_key=api_key)

    try:
        print("⏳ Extracting data (this may take a few seconds)...")
        data = await extractor.extract(url, MunicodePage)
        
        print("\n✅ Extraction Complete!")
        print("-" * 50)
        print(f"Page Title: {data.title}")
        print(f"Chapter: {data.chapter_id}")
        print(f"Found {len(data.sections)} sections.")
        
        for section in data.sections[:3]: # Show first 3
            print(f"\n[{section.section_id}] {section.title}")
            print(f"{section.content[:100]}...")
            if len(section.content) > 100:
                print("...")
        
        print("-" * 50)
        if len(data.sections) > 0:
             print("SUCCESS: Retrieved structured sections.")
        else:
             print("WARNING: No sections found. Extraction might need tuning.")

    except Exception as e:
        print(f"\n❌ Extraction Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
