"""Verification script for Phase 2 APIs."""

import asyncio
import os
import sys
from unittest.mock import MagicMock, AsyncMock

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# --- MOCKS ---
sys.modules['supabase'] = MagicMock()
sys.modules['llm_common'] = MagicMock()

# Mock Supabase Client
class MockClient:
    def __init__(self, *args, **kwargs):
        self.table = MagicMock()

sys.modules['supabase'].Client = MockClient
sys.modules['supabase'].create_client = MagicMock(return_value=MockClient())

# Mock WebSearchClient
class MockWebSearchClient:
    def __init__(self, *args, **kwargs):
        pass
    async def search(self, query, num_results=3):
        return [
            MagicMock(
                title=f"Result for {query}",
                url="https://example.gov/meetings",
                snippet="Meeting agenda..."
            )
        ]

sys.modules['llm_common'].WebSearchClient = MockWebSearchClient

# Import Services
from services.source_service import SourceService, SourceCreate, SourceUpdate
from services.auto_discovery_service import AutoDiscoveryService

async def verify_phase2():
    print("🧪 Starting Phase 2 Verification...")
    
    # 1. Verify SourceService
    print("\n--- Testing SourceService ---")
    mock_supabase = MockClient()
    
    # Mock create return
    mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [{
        "id": "source-123",
        "url": "https://sanjose.legistar.com",
        "type": "meeting",
        "status": "active"
    }]
    
    service = SourceService(mock_supabase)
    new_source = await service.create_source(SourceCreate(
        jurisdiction_id="sj-123",
        url="https://sanjose.legistar.com",
        type="meeting"
    ))
    print(f"✅ Created source: {new_source['id']}")
    
    # 2. Verify AutoDiscoveryService
    print("\n--- Testing AutoDiscoveryService ---")
    search_client = MockWebSearchClient()
    discovery_service = AutoDiscoveryService(search_client)
    
    results = await discovery_service.discover_sources("San Jose", "city")
    print(f"✅ Discovered {len(results)} potential sources")
    
    for r in results[:2]:
        print(f"  - {r['category']}: {r['title']} ({r['url']})")
        
    print("\n✅ Phase 2 Verification Complete!")

if __name__ == "__main__":
    asyncio.run(verify_phase2())
