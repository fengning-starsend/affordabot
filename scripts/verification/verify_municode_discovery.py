import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../backend"))

from services.discovery.municode_discovery import MunicodeDiscoveryService

async def main():
    print("Initializing MunicodeDiscoveryService (San Jose)...")
    service = MunicodeDiscoveryService()
    
    print("Fetching Laws (TOC)...")
    results = await service.find_laws()
    
    print(f"\nFound {len(results)} top-level sections:")
    for res in results[:10]: # Validating first 10
        print(f"- [{res.title}]({res.url})")
        print(f"  Snippet: {res.snippet}")
        print("")

if __name__ == "__main__":
    asyncio.run(main())
