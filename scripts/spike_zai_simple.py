import asyncio
import os
import sys
from pydantic import BaseModel, Field
# Adjust path to find backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.extractors.zai import ZaiExtractor

class SimplePage(BaseModel):
    title: str = Field(..., description="The title of the page")
    features: list[str] = Field(..., description="List of features mentioned")

async def main():
    api_key = os.environ.get("ZAI_API_KEY")
    if not api_key:
        print("❌ ZAI_API_KEY not found in environment.")
        return

    url = "https://iterm2.com/"
    
    print(f"🚀 Starting Z.ai Spike for Simple URL: {url}")
    
    extractor = ZaiExtractor(api_key=api_key)
    
    try:
        print("⏳ Extracting data...")
        data = await extractor.extract(url, SimplePage)
        
        print("\n✅ Extraction Complete!")
        print("-" * 50)
        print(f"Page Title: {data.title}")
        print(f"Features Found: {len(data.features)}")
        for i, feature in enumerate(data.features[:5]):
            print(f" - {feature}")
        print("-" * 50)

    except Exception as e:
        print(f"\n❌ Extraction Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
