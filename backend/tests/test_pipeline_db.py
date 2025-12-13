import pytest
from unittest.mock import MagicMock
from db.supabase_client import SupabaseDB

@pytest.fixture
def mock_client():
    return MagicMock()

@pytest.mark.asyncio
async def test_create_pipeline_run(mock_client):
    db = SupabaseDB(client=mock_client)
    mock_client.table.return_value.insert.return_value.execute.return_value.data = [{"id": "run-1"}]

    result = await db.create_pipeline_run("AB-1234", {"model": "gpt-4"}, "California")

    assert result == "run-1"
    mock_client.table.assert_called_with("pipeline_runs")
    mock_client.table.return_value.insert.assert_called_with({
        "bill_id": "AB-1234",
        "models": {"model": "gpt-4"},
        "jurisdiction": "California",
        "status": "running"
    })

@pytest.mark.asyncio
async def test_log_pipeline_step(mock_client):
    db = SupabaseDB(client=mock_client)

    result = await db.log_pipeline_step("run-1", "step1", "gpt-4", {"foo": "bar"})

    assert result is True
    mock_client.table.assert_called_with("pipeline_steps")
    mock_client.table.return_value.insert.assert_called_with({
        "run_id": "run-1",
        "step_name": "step1",
        "model": "gpt-4",
        "data": {"foo": "bar"}
    })

@pytest.mark.asyncio
async def test_update_pipeline_run_status(mock_client):
    db = SupabaseDB(client=mock_client)

    result = await db.update_pipeline_run_status("run-1", "completed")

    assert result is True
    mock_client.table.assert_called_with("pipeline_runs")

    # Check update call arguments
    args, _ = mock_client.table.return_value.update.call_args
    assert args[0]["status"] == "completed"
    assert "updated_at" in args[0]

    mock_client.table.return_value.update.return_value.eq.assert_called_with("id", "run-1")
