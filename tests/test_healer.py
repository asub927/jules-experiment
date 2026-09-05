"""
Tests for Agent 4: Ephemeral Runner & Self-Healing Agent.
"""

from fastapi.testclient import TestClient
from target_service.app import app
from src.agents.introspector import MCPIntrospectorAgent
from src.agents.grapher import DependencyGrapherAgent
from src.agents.synthesizer import PlaywrightSynthesizerAgent
from src.agents.healer import EphemeralRunnerHealerAgent

client = TestClient(app)

def test_self_healing_loop():
    mcp_res = client.post("/mcp", json={"jsonrpc": "2.0", "method": "tools/list", "id": 1}).json()
    catalog = MCPIntrospectorAgent().introspect_from_jsonrpc_response(mcp_res)
    dag = DependencyGrapherAgent().build_dag(catalog)
    synthesizer = PlaywrightSynthesizerAgent()

    healer = EphemeralRunnerHealerAgent(max_iterations=3)
    result = healer.run_suite_simulated(catalog, dag, synthesizer, mock_failure_first_attempt=True)

    assert result.success is True
    assert result.self_healed is True
    assert result.iterations == 2
    assert len(result.patch_recommendations) > 0
    assert "WGD-1234" in result.files["tests/api_regression.spec.ts"]
