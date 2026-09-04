"""
Agent 1: MCP Introspector Agent
Introspects target MCP servers (via stdio, HTTP/SSE) or OpenAPI schemas and normalizes into ToolCatalog.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import httpx
import json

class ToolParameter(BaseModel):
    name: str
    type: str
    description: Optional[str] = None
    required: bool = False
    pattern: Optional[str] = None
    enum: Optional[List[str]] = None
    minimum: Optional[float] = None
    items_type: Optional[str] = None

class EndpointSignature(BaseModel):
    tool_name: str
    description: str
    path: str
    method: str
    parameters: List[ToolParameter] = []
    input_schema: Dict[str, Any] = {}
    auth_required: bool = False
    roles_allowed: List[str] = []

class ToolCatalog(BaseModel):
    server_name: str
    version: str
    endpoints: List[EndpointSignature]
    raw_tools: List[Dict[str, Any]]

class MCPIntrospectorAgent:
    """Agent responsible for introspecting target MCP server and converting raw tool lists to a ToolCatalog."""

    def __init__(self, server_url: Optional[str] = None):
        self.server_url = server_url or "http://localhost:8000/mcp"

    def introspect_from_jsonrpc_response(self, response_data: Dict[str, Any]) -> ToolCatalog:
        """Parses a jsonrpc tools/list result into a normalized ToolCatalog."""
        tools = response_data.get("result", {}).get("tools", [])
        endpoints: List[EndpointSignature] = []

        for tool in tools:
            name = tool.get("name", "")
            description = tool.get("description", "")
            path = tool.get("path", f"/{name}")
            method = tool.get("method", "POST").upper()
            input_schema = tool.get("inputSchema", {})
            auth = tool.get("auth", {})

            properties = input_schema.get("properties", {})
            required_fields = input_schema.get("required", [])

            parsed_params: List[ToolParameter] = []
            for param_name, param_info in properties.items():
                items_type = None
                if param_info.get("type") == "array" and "items" in param_info:
                    items_type = param_info["items"].get("type")

                param = ToolParameter(
                    name=param_name,
                    type=param_info.get("type", "string"),
                    description=param_info.get("description"),
                    required=param_name in required_fields,
                    pattern=param_info.get("pattern"),
                    enum=param_info.get("enum"),
                    minimum=param_info.get("minimum"),
                    items_type=items_type
                )
                parsed_params.append(param)

            signature = EndpointSignature(
                tool_name=name,
                description=description,
                path=path,
                method=method,
                parameters=parsed_params,
                input_schema=input_schema,
                auth_required=auth.get("required", True),
                roles_allowed=auth.get("roles", ["user"])
            )
            endpoints.append(signature)

        return ToolCatalog(
            server_name="Target MCP Microservice",
            version="1.0.0",
            endpoints=endpoints,
            raw_tools=tools
        )

    def introspect_http(self, url: Optional[str] = None) -> ToolCatalog:
        target = url or self.server_url
        with httpx.Client() as client:
            resp = client.post(target, json={"jsonrpc": "2.0", "method": "tools/list", "id": 1})
            resp.raise_for_status()
            return self.introspect_from_jsonrpc_response(resp.json())
