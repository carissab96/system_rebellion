import asyncio
import pytest

# Entry points under triage/manager
from app.ai_agents.sir_hawkington.triage_engine import process_metrics_through_triage
from app.ai_agents.agent_manager import get_agent_manager

@pytest.mark.asyncio
async def test_manager_process_metrics_returns_agent_processing():
    mgr = await get_agent_manager()
    metrics = {
        "timestamp": "2025-08-18T00:00:00Z",
        "cpu_usage": 42.0,
        "memory_usage": 61.0,
        "disk_usage": 33.0,
        "network_sent_rate": 1000,
        "network_recv_rate": 2000,
    }
    enhanced = await mgr.process_metrics_through_agents(metrics, user_context={"routed_by":"unit_test"})
    assert isinstance(enhanced, dict)
    assert "agent_processing" in enhanced, "manager must attach agent_processing metadata"
    ap = enhanced["agent_processing"]
    for key in ("successful_agents","failed_agents","processing_time","total_agents","active_agents","processing_mode","routed_by"):
        assert key in ap

@pytest.mark.asyncio
async def test_triage_then_manager_flow():
    metrics = {
        "cpu_usage": 55.5,
        "memory_usage": 72.3,
        "disk_usage": 45.8,
        "network_sent_rate": 1024,
        "network_recv_rate": 2048,
        "timestamp": "2025-08-18T00:00:00Z",
    }
    # Full triage entry point should route to Agent Manager for normal ops
    result = await process_metrics_through_triage(metrics, user_id="test_user")
    assert isinstance(result, dict)
    assert "triage_decision" in result
    # When routing to normal ops, downstream manager output should be present under routing results as needed
    # (Exact shape depends on triage decision thresholds, so we check non-crashy path.)
