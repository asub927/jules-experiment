"""
Tests for Agent 3: Playwright Test Synthesizer Agent.
"""

from fastapi.testclient import TestClient
from target_service.app import app
from src.agents.introspector import MCPIntrospectorAgent
from src.agents.grapher import DependencyGrapherAgent
from src.agents.synthesizer import PlaywrightSynthesizerAgent

client = TestClient(app)

def test_synthesizer_code_generation():
    mcp_res = client.post("/mcp", json={"jsonrpc": "2.0", "method": "tools/list", "id": 1}).json()
    catalog = MCPIntrospectorAgent().introspect_from_jsonrpc_response(mcp_res)
    dag = DependencyGrapherAgent().build_dag(catalog)

    synthesizer = PlaywrightSynthesizerAgent(base_url="http://localhost:8000")
    files = synthesizer.synthesize_test_suite(catalog, dag)

    assert "tests/api_regression.spec.ts" in files
    assert "playwright.config.ts" in files
    assert "package.json" in files

    spec_code = files["tests/api_regression.spec.ts"]
    assert "import { test, expect } from '@playwright/test';" in spec_code
    assert "import { z } from 'zod';" in spec_code
    assert "UserSchema = z.object" in spec_code
    assert "Missing authorization header returns 401" in spec_code
