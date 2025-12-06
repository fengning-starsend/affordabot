"""Web search usage examples."""

import asyncio
import os

from llm_common import WebSearchClient


async def example_basic_search() -> None:
    """Example: Basic web search."""
    print("\n=== Basic Web Search ===\n")

    client = WebSearchClient(
        api_key=os.getenv("ZAI_API_KEY", "your-zai-key"),
        cache_backend="memory",
        cache_ttl=3600,  # 1 hour
    )

    # Search for California legislation
    results = await client.search(
        query="California AB 1234 housing regulations",
        count=5,
        domains=["*.gov"],
        recency="1y",
    )

    print(f"Query: {results.query}")
    print(f"Total Results: {results.total_results}")
    print(f"Search Time: {results.search_time_ms}ms")
    print(f"Cached: {results.cached}")
    print(f"Cost: ${results.cost_usd:.4f}")

    print("\nResults:")
    for i, result in enumerate(results.results, 1):
        print(f"\n{i}. {result.title}")
        print(f"   URL: {result.url}")
        print(f"   Snippet: {result.snippet[:100]}...")


async def example_caching_demonstration() -> None:
    """Example: Demonstrate caching benefits."""
    print("\n=== Caching Demonstration ===\n")

    client = WebSearchClient(
        api_key=os.getenv("ZAI_API_KEY", "your-zai-key"),
        cache_backend="memory",
        cache_ttl=3600,
    )

    query = "California housing legislation 2024"

    # First search (cache miss)
    print("First search (cache miss):")
    result1 = await client.search(query, count=10)
    print(f"Cached: {result1.cached}")
    print(f"Cost: ${result1.cost_usd:.4f}")
    print(f"Search Time: {result1.search_time_ms}ms")

    # Second search (cache hit)
    print("\nSecond search (cache hit):")
    result2 = await client.search(query, count=10)
    print(f"Cached: {result2.cached}")
    print(f"Cost: ${result2.cost_usd:.4f}")
    print(f"Search Time: {result2.search_time_ms}ms")

    # Print cache stats
    print("\nCache Statistics:")
    stats = client.get_cache_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")


async def example_bulk_legislation_search() -> None:
    """Example: Search for multiple bills with caching."""
    print("\n=== Bulk Legislation Search ===\n")

    client = WebSearchClient(
        api_key=os.getenv("ZAI_API_KEY", "your-zai-key"),
        cache_backend="memory",
    )

    # Simulate searching for multiple bills
    bills = ["AB 1234", "SB 567", "AB 890", "AB 1234"]  # Note: AB 1234 repeated

    for bill in bills:
        query = f"California {bill} housing regulations"
        print(f"\nSearching: {query}")

        results = await client.search(query, count=5, domains=["*.gov"], recency="1y")

        print(f"Results: {results.total_results}")
        print(f"Cached: {results.cached}")
        print(f"Cost: ${results.cost_usd:.4f}")

    # Print final stats
    print("\n=== Final Statistics ===")
    stats = client.get_cache_stats()
    print(f"Total Searches: {stats['total_searches']}")
    print(f"Cache Hits: {stats['cache_hits']}")
    print(f"Cache Hit Rate: {stats['hit_rate_percent']}%")
    print(f"Total Cost: ${stats['total_cost_usd']:.2f}")
    print(f"Saved from Cache: ${stats['saved_cost_usd']:.2f}")

    await client.close()


async def example_with_supabase() -> None:
    """Example: Using Supabase cache backend."""
    print("\n=== Supabase Cache Example ===\n")

    # Note: Requires supabase client
    try:
        from supabase import create_client

        supabase = create_client(
            os.getenv("SUPABASE_URL", "your-url"),
            os.getenv("SUPABASE_KEY", "your-key"),
        )

        client = WebSearchClient(
            api_key=os.getenv("ZAI_API_KEY", "your-zai-key"),
            cache_backend="supabase",
            cache_ttl=86400,  # 24 hours
            supabase_client=supabase,
        )

        # Searches will be cached in Supabase
        results = await client.search(
            query="Federal housing policy changes 2024", count=10, recency="1y"
        )

        print(f"Results: {results.total_results}")
        print(f"Cached: {results.cached}")

        await client.close()

    except ImportError:
        print("Supabase not installed. Install with: pip install supabase")


async def main() -> None:
    """Run all examples."""
    await example_basic_search()
    await example_caching_demonstration()
    await example_bulk_legislation_search()
    await example_with_supabase()


if __name__ == "__main__":
    asyncio.run(main())
