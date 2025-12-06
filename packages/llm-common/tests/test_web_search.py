"""Tests for web search client."""

import pytest

from llm_common import WebSearchClient


def test_web_search_client_initialization():
    """Test WebSearchClient initializes correctly."""
    client = WebSearchClient(
        api_key="test-key", cache_backend="memory", cache_ttl=3600
    )

    assert client.api_key == "test-key"
    assert client.cache_backend == "memory"
    assert client.cache_ttl == 3600
    assert client._total_searches == 0
    assert client._cache_hits == 0
    assert client._cache_misses == 0


def test_generate_cache_key():
    """Test cache key generation."""
    client = WebSearchClient(api_key="test-key")

    # Same parameters should generate same key
    key1 = client._generate_cache_key("test query", 10, None, None, {})
    key2 = client._generate_cache_key("test query", 10, None, None, {})
    assert key1 == key2

    # Different query should generate different key
    key3 = client._generate_cache_key("different query", 10, None, None, {})
    assert key1 != key3

    # Different count should generate different key
    key4 = client._generate_cache_key("test query", 20, None, None, {})
    assert key1 != key4

    # Case-insensitive query
    key5 = client._generate_cache_key("Test Query", 10, None, None, {})
    assert key1 == key5


def test_cache_stats_initial():
    """Test initial cache statistics."""
    client = WebSearchClient(api_key="test-key")

    stats = client.get_cache_stats()

    assert stats["total_searches"] == 0
    assert stats["cache_hits"] == 0
    assert stats["cache_misses"] == 0
    assert stats["hit_rate"] == 0.0
    assert stats["total_cost_usd"] == 0.0


def test_cache_stats_after_searches():
    """Test cache statistics after searches."""
    client = WebSearchClient(api_key="test-key")

    # Simulate cache miss
    client._cache_misses += 1
    client._total_searches += 1
    client._total_cost += client.COST_PER_SEARCH

    # Simulate cache hit
    client._cache_hits += 1
    client._total_searches += 1

    stats = client.get_cache_stats()

    assert stats["total_searches"] == 2
    assert stats["cache_hits"] == 1
    assert stats["cache_misses"] == 1
    assert stats["hit_rate"] == 0.5
    assert stats["hit_rate_percent"] == 50.0
    assert stats["total_cost_usd"] == 0.01
    assert stats["saved_cost_usd"] == 0.01


def test_reset_stats():
    """Test resetting statistics."""
    client = WebSearchClient(api_key="test-key")

    # Add some stats
    client._total_searches = 10
    client._cache_hits = 5
    client._cache_misses = 5
    client._total_cost = 0.05

    # Reset
    client.reset_stats()

    assert client._total_searches == 0
    assert client._cache_hits == 0
    assert client._cache_misses == 0
    assert client._total_cost == 0.0


@pytest.mark.asyncio
async def test_search_with_mock(mocker):
    """Test search with mocked HTTP client."""
    client = WebSearchClient(api_key="test-key", cache_backend="memory")

    # Mock HTTP response
    mock_response = mocker.MagicMock()
    mock_response.json.return_value = {
        "results": [
            {
                "url": "https://example.com",
                "title": "Example",
                "snippet": "Test snippet",
                "domain": "example.com",
            }
        ]
    }

    mocker.patch.object(client.client, "post", return_value=mock_response)

    # Perform search
    results = await client.search("test query", count=10)

    assert results.query == "test query"
    assert len(results.results) == 1
    assert results.results[0].url == "https://example.com"
    assert results.cached is False
    assert results.cost_usd == client.COST_PER_SEARCH

    # Check stats
    stats = client.get_cache_stats()
    assert stats["cache_misses"] == 1
    assert stats["total_searches"] == 1


@pytest.mark.asyncio
async def test_search_caching(mocker):
    """Test that searches are cached."""
    client = WebSearchClient(api_key="test-key", cache_backend="memory")

    # Mock HTTP response
    mock_response = mocker.MagicMock()
    mock_response.json.return_value = {
        "results": [
            {
                "url": "https://example.com",
                "title": "Example",
                "snippet": "Test",
                "domain": "example.com",
            }
        ]
    }

    mock_post = mocker.patch.object(client.client, "post", return_value=mock_response)

    # First search (cache miss)
    result1 = await client.search("test query", count=10)
    assert result1.cached is False
    assert mock_post.call_count == 1

    # Second search with same parameters (cache hit)
    result2 = await client.search("test query", count=10)
    assert result2.cached is True
    assert mock_post.call_count == 1  # Still 1, no new API call

    # Check stats
    stats = client.get_cache_stats()
    assert stats["total_searches"] == 2
    assert stats["cache_hits"] == 1
    assert stats["cache_misses"] == 1
    assert stats["hit_rate_percent"] == 50.0


@pytest.mark.asyncio
async def test_close():
    """Test closing the client."""
    client = WebSearchClient(api_key="test-key")

    await client.close()
    # Should not raise any errors
