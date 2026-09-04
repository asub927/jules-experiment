"""
Full End-to-End Orchestration & Verification Test for API Automation Factory.
Executes Agent 1 (Introspection) -> Agent 2 (Graphing) -> Agent 3 (Synthesis) -> Agent 4 (Execution & Self-Healing).
"""

from fastapi.testclient import TestClient
from target_service.app import app
from src.agents.introspector import MCPIntrospectorAgent
from src.agents.grapher import DependencyGrapherAgent
from src.agents.synthesizer import PlaywrightSynthesizerAgent
from src.agents.healer import EphemeralRunnerHealerAgent

client = TestClient(app)

def test_full_e2e_agent_swarm_pipeline():
    # 1. Introspect target server via MCP JSON-RPC
    mcp_res = client.post("/mcp", json={"jsonrpc": "2.0", "method": "tools/list", "id": 1}).json()
    introspector = MCPIntrospectorAgent()
    catalog = introspector.introspect_from_jsonrpc_response(mcp_res)
    assert len(catalog.endpoints) == 8

    # 2. Generate Dependency Graph
    grapher = DependencyGrapherAgent()
    dag = grapher.build_dag(catalog)
    assert len(dag.execution_tiers) >= 3
    assert len(dag.state_handoffs) > 0

    # 3. Synthesize Playwright TypeScript suite
    synthesizer = PlaywrightSynthesizerAgent(base_url="http://localhost:8000")
    files = synthesizer.synthesize_test_suite(catalog, dag)
    assert "tests/api_regression.spec.ts" in files

    # 4. Execute Self-Healing Ephemeral Runner
    healer = EphemeralRunnerHealerAgent(max_iterations=3)
    run_result = healer.run_suite_simulated(catalog, dag, synthesizer, mock_failure_first_attempt=True)

    assert run_result.success is True
    assert run_result.self_healed is True
    assert run_result.iterations == 2
    assert "WGD-1234" in run_result.files["tests/api_regression.spec.ts"]
    assert len(run_result.patch_recommendations) > 0
