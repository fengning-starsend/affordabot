"""Web search client with intelligent caching."""

import hashlib
import json
import time
from datetime import datetime, timedelta
from typing import Any, Literal, Optional

import httpx
from cachetools import TTLCache

from llm_common.core import CacheError, LLMError, WebSearchResponse, WebSearchResult


class WebSearchClient:
    """Web search client with z.ai integration and caching."""

    BASE_URL = "https://open.z.ai/api/v1"
    COST_PER_SEARCH = 0.01  # $0.01 per search

    def __init__(
        self,
        api_key: str,
        cache_backend: Literal["memory", "supabase"] = "memory",
        cache_ttl: int = 86400,  # 24 hours
        supabase_client: Optional[Any] = None,
    ) -> None:
        """Initialize web search client.

        Args:
            api_key: z.ai API key
            cache_backend: Cache backend to use ("memory" or "supabase")
            cache_ttl: Cache TTL in seconds (default 24 hours)
            supabase_client: Supabase client instance (required if backend="supabase")
        """
        self.api_key = api_key
        self.cache_backend = cache_backend
        self.cache_ttl = cache_ttl
        self.supabase = supabase_client

        # In-memory cache (used for both backends as L1 cache)
        self._memory_cache: TTLCache = TTLCache(maxsize=1000, ttl=cache_ttl)

        # HTTP client
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30.0,
        )

        # Metrics
        self._total_searches = 0
        self._cache_hits = 0
        self._cache_misses = 0
        self._total_cost = 0.0

    async def search(
        self,
        query: str,
        count: int = 10,
        domains: Optional[list[str]] = None,
        recency: Optional[str] = None,
        **kwargs: Any,
    ) -> WebSearchResponse:
        """Perform web search with caching.

        Args:
            query: Search query
            count: Number of results to return
            domains: List of domains to filter (e.g., ["*.gov"])
            recency: Recency filter (e.g., "1d", "1w", "1m", "1y")
            **kwargs: Additional search parameters

        Returns:
            Web search response with results

        Raises:
            LLMError: If search fails
        """
        # Generate cache key
        cache_key = self._generate_cache_key(query, count, domains, recency, kwargs)

        # Check L1 cache (memory)
        cached = self._memory_cache.get(cache_key)
        if cached:
            self._cache_hits += 1
            self._total_searches += 1
            cached["cached"] = True
            cached["created_at"] = datetime.fromisoformat(cached["created_at"])
            return WebSearchResponse(**cached)

        # Check L2 cache (Supabase) if enabled
        if self.cache_backend == "supabase" and self.supabase:
            cached = await self._get_from_supabase(cache_key)
            if cached:
                self._cache_hits += 1
                self._total_searches += 1
                # Warm L1 cache
                self._memory_cache[cache_key] = cached
                cached["cached"] = True
                cached["created_at"] = datetime.fromisoformat(cached["created_at"])
                return WebSearchResponse(**cached)

        # Cache miss - perform actual search
        self._cache_misses += 1
        self._total_searches += 1
        self._total_cost += self.COST_PER_SEARCH

        start_time = time.time()

        try:
            response = await self.client.post(
                "/search",
                json={
                    "query": query,
                    "count": count,
                    "domains": domains,
                    "recency": recency,
                    **kwargs,
                },
            )
            response.raise_for_status()
            data = response.json()

            search_time_ms = int((time.time() - start_time) * 1000)

            # Parse results
            results = [
                WebSearchResult(
                    url=r["url"],
                    title=r["title"],
                    snippet=r.get("snippet", ""),
                    content=r.get("content"),
                    published_date=r.get("published_date"),
                    domain=r.get("domain", ""),
                    relevance_score=r.get("relevance_score"),
                )
                for r in data.get("results", [])
            ]

            search_response = WebSearchResponse(
                query=query,
                results=results,
                total_results=len(results),
                search_time_ms=search_time_ms,
                cached=False,
                cost_usd=self.COST_PER_SEARCH,
                provider="zai",
            )

            # Cache the response
            response_dict = search_response.model_dump()
            response_dict["created_at"] = response_dict["created_at"].isoformat()

            # Store in L1 cache (memory)
            self._memory_cache[cache_key] = response_dict

            # Store in L2 cache (Supabase) if enabled
            if self.cache_backend == "supabase" and self.supabase:
                await self._store_in_supabase(cache_key, response_dict)

            return search_response

        except httpx.HTTPStatusError as e:
            raise LLMError(f"Search failed with status {e.response.status_code}: {e}", provider="zai")
        except Exception as e:
            raise LLMError(f"Search failed: {e}", provider="zai")

    def _generate_cache_key(
        self,
        query: str,
        count: int,
        domains: Optional[list[str]],
        recency: Optional[str],
        kwargs: dict[str, Any],
    ) -> str:
        """Generate cache key from search parameters.

        Args:
            query: Search query
            count: Number of results
            domains: Domain filters
            recency: Recency filter
            kwargs: Additional parameters

        Returns:
            Cache key (SHA256 hash)
        """
        # Create deterministic representation
        cache_data = {
            "query": query.lower().strip(),
            "count": count,
            "domains": sorted(domains) if domains else None,
            "recency": recency,
            **kwargs,
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(cache_str.encode()).hexdigest()

    async def _get_from_supabase(self, cache_key: str) -> Optional[dict[str, Any]]:
        """Retrieve cached result from Supabase.

        Args:
            cache_key: Cache key

        Returns:
            Cached response dict if found and not expired, None otherwise
        """
        if not self.supabase:
            return None

        try:
            result = (
                self.supabase.table("web_search_cache")
                .select("*")
                .eq("cache_key", cache_key)
                .single()
                .execute()
            )

            if not result.data:
                return None

            # Check if expired
            created_at = datetime.fromisoformat(result.data["created_at"])
            if datetime.utcnow() - created_at > timedelta(seconds=self.cache_ttl):
                # Expired - delete from cache
                await self._delete_from_supabase(cache_key)
                return None

            return result.data["response"]

        except Exception:
            # Cache errors should not break search
            return None

    async def _store_in_supabase(
        self, cache_key: str, response: dict[str, Any]
    ) -> None:
        """Store result in Supabase cache.

        Args:
            cache_key: Cache key
            response: Response to cache
        """
        if not self.supabase:
            return

        try:
            self.supabase.table("web_search_cache").upsert(
                {
                    "cache_key": cache_key,
                    "query": response["query"],
                    "response": response,
                    "created_at": response["created_at"],
                }
            ).execute()
        except Exception as e:
            # Cache errors should not break search
            raise CacheError(f"Failed to store in cache: {e}", provider="supabase")

    async def _delete_from_supabase(self, cache_key: str) -> None:
        """Delete expired entry from Supabase cache.

        Args:
            cache_key: Cache key
        """
        if not self.supabase:
            return

        try:
            self.supabase.table("web_search_cache").delete().eq(
                "cache_key", cache_key
            ).execute()
        except Exception:
            # Ignore deletion errors
            pass

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Cache statistics including hit rate and cost savings
        """
        hit_rate = (
            self._cache_hits / self._total_searches if self._total_searches > 0 else 0.0
        )

        # Calculate cost savings from cache hits
        saved_cost = self._cache_hits * self.COST_PER_SEARCH

        return {
            "total_searches": self._total_searches,
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
            "hit_rate": round(hit_rate, 3),
            "hit_rate_percent": round(hit_rate * 100, 1),
            "total_cost_usd": round(self._total_cost, 2),
            "saved_cost_usd": round(saved_cost, 2),
            "effective_cost_usd": round(self._total_cost, 2),
        }

    def reset_stats(self) -> None:
        """Reset cache statistics."""
        self._total_searches = 0
        self._cache_hits = 0
        self._cache_misses = 0
        self._total_cost = 0.0

    async def close(self) -> None:
        """Close HTTP client."""
        await self.client.aclose()
