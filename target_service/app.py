"""
Target MCP / REST Server microservice used for testing API Automation Factory.
Includes REST endpoints and an MCP JSON-RPC handler.
"""

from fastapi import FastAPI, Header, HTTPException, Response, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import re

app = FastAPI(
    title="Target Enterprise API & MCP Microservice",
    version="1.0.0",
    description="Target service with Users, Items, and Orders domains for MCP Introspection and Playwright regression testing."
)

# In-memory storage
USERS_DB: Dict[str, Dict[str, Any]] = {}
ITEMS_DB: Dict[str, Dict[str, Any]] = {}
ORDERS_DB: Dict[str, Dict[str, Any]] = {}

VALID_SKU_REGEX = re.compile(r"^[A-Z]{3}-\d{4}$")

# Models
class UserCreate(BaseModel):
    name: str = Field(..., example="Alice Smith")
    email: str = Field(..., example="alice@example.com")
    role: str = Field("user", example="user")

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    created_at: str

class ItemCreate(BaseModel):
    name: str
    sku: str = Field(..., description="Must follow format ABC-1234")
    price: float = Field(..., gt=0)
    category: str

class ItemResponse(BaseModel):
    id: str
    name: str
    sku: str
    price: float
    category: str
    created_at: str

class OrderCreate(BaseModel):
    user_id: str
    item_ids: List[str]
    shipping_address: str

class OrderResponse(BaseModel):
    id: str
    user_id: str
    item_ids: List[str]
    total_amount: float
    status: str
    created_at: str


# Helper auth checker
def verify_auth(authorization: Optional[str] = Header(None), required_role: str = "user"):
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer realm='Access to target API'"}
        )
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid token scheme",
            headers={"WWW-Authenticate": "Bearer realm='Access to target API'"}
        )
    token = authorization.replace("Bearer ", "")
    if token == "expired_token":
        raise HTTPException(
            status_code=401,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer realm='Access to target API', error='invalid_token'"}
        )
    if token == "user_token" and required_role == "admin":
        raise HTTPException(status_code=403, detail="Forbidden: Insufficient privileges")
    if token not in ["admin_token", "user_token"]:
        raise HTTPException(status_code=401, detail="Invalid token")

# Health check
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "target-mcp-api"}

# USERS DOMAIN
@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, authorization: Optional[str] = Header(None)):
    verify_auth(authorization, required_role="user")
    user_id = f"usr_{uuid.uuid4().hex[:8]}"
    created_at = datetime.now(timezone.utc).isoformat()
    record = {
        "id": user_id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "created_at": created_at
    }
    USERS_DB[user_id] = record
    return record

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: str, authorization: Optional[str] = Header(None)):
    verify_auth(authorization, required_role="user")
    if user_id not in USERS_DB:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return USERS_DB[user_id]

@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: str, authorization: Optional[str] = Header(None)):
    verify_auth(authorization, required_role="admin")
    if user_id not in USERS_DB:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    del USERS_DB[user_id]
    return Response(status_code=204)

# ITEMS DOMAIN
@app.post("/items", response_model=ItemResponse, status_code=201)
def create_item(item: ItemCreate, authorization: Optional[str] = Header(None)):
    verify_auth(authorization, required_role="admin")
    if not VALID_SKU_REGEX.match(item.sku):
        raise HTTPException(
            status_code=422,
            detail=f"Field 'sku' violates format constraint. Expected regex '^[A-Z]{{3}}-\\d{{4}}$', got '{item.sku}'"
        )
    item_id = f"item_{uuid.uuid4().hex[:8]}"
    created_at = datetime.now(timezone.utc).isoformat()
    record = {
        "id": item_id,
        "name": item.name,
        "sku": item.sku,
        "price": item.price,
        "category": item.category,
        "created_at": created_at
    }
    ITEMS_DB[item_id] = record
    return record

@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: str, authorization: Optional[str] = Header(None)):
    verify_auth(authorization, required_role="user")
    if item_id not in ITEMS_DB:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return ITEMS_DB[item_id]

@app.get("/items", response_model=List[ItemResponse])
def list_items(authorization: Optional[str] = Header(None)):
    verify_auth(authorization, required_role="user")
    return list(ITEMS_DB.values())

# ORDERS DOMAIN
@app.post("/orders", response_model=OrderResponse, status_code=201)
def create_order(order: OrderCreate, authorization: Optional[str] = Header(None)):
    verify_auth(authorization, required_role="user")
    if order.user_id not in USERS_DB:
        raise HTTPException(status_code=400, detail=f"Referenced user_id '{order.user_id}' does not exist")

    total = 0.0
    for item_id in order.item_ids:
        if item_id not in ITEMS_DB:
            raise HTTPException(status_code=400, detail=f"Referenced item_id '{item_id}' does not exist")
        total += ITEMS_DB[item_id]["price"]

    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    created_at = datetime.now(timezone.utc).isoformat()
    record = {
        "id": order_id,
        "user_id": order.user_id,
        "item_ids": order.item_ids,
        "total_amount": round(total, 2),
        "status": "pending",
        "created_at": created_at
    }
    ORDERS_DB[order_id] = record
    return record

@app.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: str, authorization: Optional[str] = Header(None)):
    verify_auth(authorization, required_role="user")
    if order_id not in ORDERS_DB:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    return ORDERS_DB[order_id]

@app.delete("/orders/{order_id}", status_code=204)
def delete_order(order_id: str, authorization: Optional[str] = Header(None)):
    verify_auth(authorization, required_role="user")
    if order_id not in ORDERS_DB:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    del ORDERS_DB[order_id]
    return Response(status_code=204)

# MCP JSON-RPC ENDPOINT FOR INTROSPECTION / INVOCATION
MCP_TOOLS = [
    {
        "name": "create_user",
        "description": "Creates a new user in the system.",
        "path": "/users",
        "method": "POST",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "email": {"type": "string", "format": "email"},
                "role": {"type": "string", "enum": ["admin", "user"]}
            },
            "required": ["name", "email"]
        },
        "auth": {"required": True, "roles": ["user", "admin"]}
    },
    {
        "name": "get_user",
        "description": "Retrieves user details by user ID.",
        "path": "/users/{user_id}",
        "method": "GET",
        "inputSchema": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "Foreign key reference to user.id"}
            },
            "required": ["user_id"]
        },
        "auth": {"required": True, "roles": ["user", "admin"]}
    },
    {
        "name": "delete_user",
        "description": "Deletes a user account.",
        "path": "/users/{user_id}",
        "method": "DELETE",
        "inputSchema": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string"}
            },
            "required": ["user_id"]
        },
        "auth": {"required": True, "roles": ["admin"]}
    },
    {
        "name": "create_item",
        "description": "Creates a new item inventory catalog record.",
        "path": "/items",
        "method": "POST",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "sku": {"type": "string", "pattern": "^[A-Z]{3}-\\d{4}$", "description": "Must match regex ABC-1234"},
                "price": {"type": "number", "minimum": 0.01},
                "category": {"type": "string"}
            },
            "required": ["name", "sku", "price", "category"]
        },
        "auth": {"required": True, "roles": ["admin"]}
    },
    {
        "name": "get_item",
        "description": "Retrieves item details by item ID.",
        "path": "/items/{item_id}",
        "method": "GET",
        "inputSchema": {
            "type": "object",
            "properties": {
                "item_id": {"type": "string"}
            },
            "required": ["item_id"]
        },
        "auth": {"required": True, "roles": ["user", "admin"]}
    },
    {
        "name": "create_order",
        "description": "Creates an order linking a user ID and list of item IDs.",
        "path": "/orders",
        "method": "POST",
        "inputSchema": {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "Foreign key reference to user.id"},
                "item_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of foreign key references to item.id"
                },
                "shipping_address": {"type": "string"}
            },
            "required": ["user_id", "item_ids", "shipping_address"]
        },
        "auth": {"required": True, "roles": ["user", "admin"]}
    },
    {
        "name": "get_order",
        "description": "Retrieves order details by order ID.",
        "path": "/orders/{order_id}",
        "method": "GET",
        "inputSchema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"}
            },
            "required": ["order_id"]
        },
        "auth": {"required": True, "roles": ["user", "admin"]}
    },
    {
        "name": "delete_order",
        "description": "Deletes an existing order.",
        "path": "/orders/{order_id}",
        "method": "DELETE",
        "inputSchema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"}
            },
            "required": ["order_id"]
        },
        "auth": {"required": True, "roles": ["user", "admin"]}
    }
]

@app.post("/mcp")
async def mcp_rpc(request: Request):
    data = await request.json()
    method = data.get("method")
    req_id = data.get("id", 1)

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": MCP_TOOLS
            }
        }
    elif method == "tools/call":
        tool_name = data.get("params", {}).get("name")
        args = data.get("params", {}).get("arguments", {})
        # Route tool call to internal handler if needed
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [{"type": "text", "text": f"Executed tool {tool_name} with args {args}"}]
            }
        }
    else:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method '{method}' not found"}
        }
