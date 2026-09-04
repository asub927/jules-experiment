"""
Tests for target MCP & REST microservice.
"""

from fastapi.testclient import TestClient
from target_service.app import app

client = TestClient(app)

def test_health_check():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

def test_mcp_tools_list():
    res = client.post("/mcp", json={"jsonrpc": "2.0", "method": "tools/list", "id": 1})
    assert res.status_code == 200
    data = res.json()
    assert "result" in data
    assert "tools" in data["result"]
    tools = data["result"]["tools"]
    tool_names = [t["name"] for t in tools]
    assert "create_user" in tool_names
    assert "create_order" in tool_names

def test_crud_flow():
    # 1. Unauthenticated request should return 401
    res = client.post("/users", json={"name": "Test User", "email": "test@example.com"})
    assert res.status_code == 401
    assert "WWW-Authenticate" in res.headers

    # 2. Create user with auth
    user_res = client.post(
        "/users",
        json={"name": "Test User", "email": "test@example.com"},
        headers={"Authorization": "Bearer user_token"}
    )
    assert user_res.status_code == 201
    user = user_res.json()
    assert user["id"].startswith("usr_")

    # 3. Create item with admin auth (and invalid SKU to test 422)
    invalid_item_res = client.post(
        "/items",
        json={"name": "Widget", "sku": "INVALID_SKU", "price": 19.99, "category": "Electronics"},
        headers={"Authorization": "Bearer admin_token"}
    )
    assert invalid_item_res.status_code == 422

    # 4. Create item with valid SKU
    valid_item_res = client.post(
        "/items",
        json={"name": "Widget", "sku": "WGD-1234", "price": 19.99, "category": "Electronics"},
        headers={"Authorization": "Bearer admin_token"}
    )
    assert valid_item_res.status_code == 201
    item = valid_item_res.json()
    assert item["id"].startswith("item_")

    # 5. Create order linking user and item
    order_res = client.post(
        "/orders",
        json={"user_id": user["id"], "item_ids": [item["id"]], "shipping_address": "123 Main St"},
        headers={"Authorization": "Bearer user_token"}
    )
    assert order_res.status_code == 201
    order = order_res.json()
    assert order["total_amount"] == 19.99
