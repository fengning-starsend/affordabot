import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../backend"))

from services.discovery.city_scrapers_discovery import CityScrapersDiscoveryService

async def main():
    print("Initializing CityScrapersDiscoveryService...")
    service = CityScrapersDiscoveryService()
    
    print("Finding meeting content for 'sanjose'...")
    results = await service.find_meeting_content("sanjose")
    
    for res in results:
        print(f"- [{res.title}]({res.url})")
        print(f"  Snippet: {res.snippet}")
        print(f"  Content: {res.content}")
        print("")

if __name__ == "__main__":
    asyncio.run(main())
