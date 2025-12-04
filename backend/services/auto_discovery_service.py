"""Service for auto-discovering sources using templates and web search."""

from __future__ import annotations
from typing import List, Dict, Any
from llm_common import WebSearchClient

QUERY_TEMPLATES = {
    "city": {
        "meetings": [
            "{name} city council meetings",
            "{name} planning commission agenda"
        ],
        "code": [
            "{name} municipal code",
            "{name} zoning ordinance"
        ],
        "permits": [
            "{name} building permits",
            "{name} planning applications"
        ]
    },
    "county": {
        "meetings": ["{name} board of supervisors"],
        "code": ["{name} county code"]
    }
}

class AutoDiscoveryService:
    def __init__(self, web_search_client: WebSearchClient):
        self.search_client = web_search_client

    async def discover_sources(self, jurisdiction_name: str, jurisdiction_type: str = "city") -> List[Dict[str, Any]]:
        """
        Run template-based discovery for a jurisdiction.
        
        Args:
            jurisdiction_name: Name of the city/county (e.g. "San Jose")
            jurisdiction_type: "city" or "county"
            
        Returns:
            List of potential sources found
        """
        templates = QUERY_TEMPLATES.get(jurisdiction_type, {})
        results = []

        for category, queries in templates.items():
            for query_template in queries:
                query = query_template.format(name=jurisdiction_name)
                
                # Run search
                search_results = await self.search_client.search(query, num_results=3)
                
                for res in search_results:
                    # Simple filtering
                    if self._is_relevant(res.url):
                        results.append({
                            "jurisdiction_name": jurisdiction_name,
                            "category": category,
                            "query": query,
                            "title": res.title,
                            "url": res.url,
                            "snippet": res.snippet
                        })
        
        return results

    def _is_relevant(self, url: str) -> bool:
        """Filter out obviously irrelevant URLs."""
        # Allow .gov, .us, and known platforms
        allowed_domains = ['.gov', '.us', 'legistar.com', 'municode.com', 'granicus.com', 'codepublishing.com']
        return any(d in url for d in allowed_domains)
