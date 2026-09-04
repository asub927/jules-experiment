"""
Tests for Agent 1: MCP Introspector Agent.
"""

from fastapi.testclient import TestClient
from target_service.app import app
from src.agents.introspector import MCPIntrospectorAgent, ToolCatalog

client = TestClient(app)

def test_introspector_with_mock_client():
    res = client.post("/mcp", json={"jsonrpc": "2.0", "method": "tools/list", "id": 1})
    assert res.status_code == 200

    agent = MCPIntrospectorAgent()
    catalog = agent.introspect_from_jsonrpc_response(res.json())

    assert isinstance(catalog, ToolCatalog)
    assert len(catalog.endpoints) == 8

    # Check create_user tool signature
    user_tool = next(ep for ep in catalog.endpoints if ep.tool_name == "create_user")
    assert user_tool.path == "/users"
    assert user_tool.method == "POST"
    assert any(p.name == "email" for p in user_tool.parameters)

    # Check create_item tool signature regex pattern constraint
    item_tool = next(ep for ep in catalog.endpoints if ep.tool_name == "create_item")
    sku_param = next(p for p in item_tool.parameters if p.name == "sku")
    assert sku_param.pattern == "^[A-Z]{3}-\\d{4}$"
