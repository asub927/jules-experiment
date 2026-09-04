"""
Tests for Agent 2: State & Dependency Grapher Agent.
"""

from fastapi.testclient import TestClient
from target_service.app import app
from src.agents.introspector import MCPIntrospectorAgent
from src.agents.grapher import DependencyGrapherAgent, ExecutionDAG

client = TestClient(app)

def test_grapher_dag_generation():
    mcp_res = client.post("/mcp", json={"jsonrpc": "2.0", "method": "tools/list", "id": 1}).json()
    introspector = MCPIntrospectorAgent()
    catalog = introspector.introspect_from_jsonrpc_response(mcp_res)

    grapher = DependencyGrapherAgent()
    dag = grapher.build_dag(catalog)

    assert isinstance(dag, ExecutionDAG)
    assert len(dag.execution_tiers) >= 3

    # Tier 0 should contain create_user and create_item
    tier_0 = dag.execution_tiers[0]
    assert "create_user" in tier_0
    assert "create_item" in tier_0

    # Tier 1 should contain create_order (since it depends on create_user and create_item)
    create_order_node = next(n for n in dag.nodes if n.tool_name == "create_order")
    assert "create_user" in create_order_node.dependencies
    assert "create_item" in create_order_node.dependencies

    # Verify state handoffs
    handoff_targets = [h.target_tool for h in dag.state_handoffs]
    assert "create_order" in handoff_targets
