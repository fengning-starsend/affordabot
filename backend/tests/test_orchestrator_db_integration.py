import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
import pytest
import asyncio
import os

# Setup paths to include backend
backend_path = str(Path(__file__).parent.parent)
sys.path.append(backend_path)

# Mock llm_common imports BEFORE importing orchestrator
# We need to ensure that when orchestrator imports these, it gets our mocks
mock_core = MagicMock()
mock_web_search = MagicMock()
mock_agents = MagicMock()

sys.modules["llm_common"] = MagicMock()
sys.modules["llm_common.core"] = mock_core
sys.modules["llm_common.web_search"] = mock_web_search
sys.modules["llm_common.agents"] = mock_agents

# Now import the module under test
from services.llm.orchestrator import AnalysisPipeline, BillAnalysis, ReviewCritique

@pytest.mark.asyncio
async def test_pipeline_db_integration():
    print("Testing Pipeline DB Integration...")

    # Mocks
    mock_llm = MagicMock()
    mock_search = MagicMock()
    mock_db = MagicMock()

    # Setup mock DB methods
    mock_db.create_pipeline_run = AsyncMock(return_value="run-123")
    mock_db.fail_pipeline_run = AsyncMock(return_value=True)
    mock_db.complete_pipeline_run = AsyncMock(return_value=True)
    mock_db.get_or_create_jurisdiction = AsyncMock(return_value="jur-123")
    mock_db.store_legislation = AsyncMock(return_value="leg-123")
    mock_db.store_impacts = AsyncMock(return_value=True)

    # Instantiate pipeline
    pipeline = AnalysisPipeline(mock_llm, mock_search, mock_db)

    # Configure the mocked ResearchAgent instance
    pipeline.research_agent.run = AsyncMock(return_value={"collected_data": [{"url": "http://test.com"}]})

    # Helper to return awaitable result
    def async_return(result):
        f = asyncio.Future()
        f.set_result(result)
        return f

    # Test Case 1: Success Path
    print("Test Case 1: Success Path")

    # Make LLM return valid objects for generate and review steps
    # Note: side_effect with iterable in AsyncMock needs awaitables
    mock_llm.chat.side_effect = [
        async_return(BillAnalysis(summary="sum", impacts=[], confidence=1.0, sources=[])), # Generate
        async_return(ReviewCritique(passed=True, critique="Good", missing_impacts=[], factual_errors=[])) # Review
    ]

    await pipeline.run("bill-1", "text", "jurisdiction", {"research": "m1", "generate": "m2", "review": "m3"})

    # Verify Create
    mock_db.create_pipeline_run.assert_called_once_with("bill-1", "jurisdiction", {"research": "m1", "generate": "m2", "review": "m3"})

    # Verify Complete
    mock_db.complete_pipeline_run.assert_called_once()
    assert mock_db.complete_pipeline_run.call_args[0][0] == "run-123"

    print("Success Path Verified.")

    # Test Case 2: Failure Path
    print("Test Case 2: Failure Path")

    # Reset mocks
    mock_db.reset_mock()
    mock_llm.reset_mock()

    mock_db.create_pipeline_run = AsyncMock(return_value="run-456")
    mock_db.fail_pipeline_run = AsyncMock(return_value=True)

    # Make LLM raise exception
    mock_llm.chat.side_effect = Exception("LLM Error")

    # We anticipate an exception
    with pytest.raises(Exception) as excinfo:
         await pipeline.run("bill-2", "text", "jurisdiction", {"research": "m1", "generate": "m2", "review": "m3"})

    assert "LLM Error" in str(excinfo.value)

    # Verify Fail
    mock_db.fail_pipeline_run.assert_called_once_with("run-456", "LLM Error")
    print("Failure Path Verified.")

if __name__ == "__main__":
    asyncio.run(test_pipeline_db_integration())
