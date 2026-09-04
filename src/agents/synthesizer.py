"""
Agent 3: Playwright Test Synthesizer Agent
Translates ToolCatalog and ExecutionDAG into idiomatic Playwright TypeScript test suites
with strict runtime Zod assertions enforcing the 4 validation pillars:
1. HTTP Method Validation
2. Endpoint & Routing Boundary Checks
3. Authentication & Authorization Scenarios
4. Strict Runtime Schema Validation with Zod
"""

from typing import Dict, Any, List, Optional
from src.agents.introspector import ToolCatalog, EndpointSignature
from src.agents.grapher import ExecutionDAG

class PlaywrightSynthesizerAgent:
    """Synthesizes Playwright TypeScript regression tests with Zod runtime validation."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def synthesize_test_suite(
        self,
        catalog: ToolCatalog,
        dag: ExecutionDAG,
        fixture_overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """Generates TypeScript Playwright test files and returns a dictionary of file path -> content."""
        fixtures = fixture_overrides or {}

        # Default synthetic fixture data (intentionally non-conforming default SKU to trigger self-healing if uncorrected)
        user_name = fixtures.get("user_name", "Automation Test User")
        user_email = fixtures.get("user_email", "auto_user@example.com")
        item_name = fixtures.get("item_name", "Enterprise Server License")
        item_sku = fixtures.get("item_sku", "SKU9999")  # Missing dash - will fail regex ^[A-Z]{3}-\d{4}$
        item_price = fixtures.get("item_price", 299.99)
        item_category = fixtures.get("item_category", "Software")

        spec_content = f"""import {{ test, expect }} from '@playwright/test';
import {{ z }} from 'zod';

const BASE_URL = process.env.BASE_URL || '{self.base_url}';
const USER_TOKEN = 'user_token';
const ADMIN_TOKEN = 'admin_token';

// Zod Runtime Schemas
export const UserSchema = z.object({{
  id: z.string(),
  name: z.string(),
  email: z.string(),
  role: z.string(),
  created_at: z.string()
}}).strict();

export const ItemSchema = z.object({{
  id: z.string(),
  name: z.string(),
  sku: z.string().regex(/^[A-Z]{{3}}-\\d{{4}}$/),
  price: z.number().positive(),
  category: z.string(),
  created_at: z.string()
}}).strict();

export const OrderSchema = z.object({{
  id: z.string(),
  user_id: z.string(),
  item_ids: z.array(z.string()),
  total_amount: z.number().positive(),
  status: z.enum(['pending', 'processing', 'completed', 'cancelled']),
  created_at: z.string()
}}).strict();

export const ErrorResponseSchema = z.object({{
  detail: z.union([z.string(), z.array(z.any())])
}});

test.describe('API Automation Factory - Four Pillar Playwright Regression Suite', () => {{
  let createdUserId: string;
  let createdItemId: string;
  let createdOrderId: string;

  // PILLAR 1 & 4: CRUD Execution & Strict Zod Validation (Tier 0 & Tier 1)
  test('Tier 0: Create User with strict Zod assertion', async ({{ request }}) => {{
    const response = await request.post(`${{BASE_URL}}/users`, {{
      headers: {{
        'Authorization': `Bearer ${{USER_TOKEN}}`,
        'Content-Type': 'application/json'
      }},
      data: {{
        name: '{user_name}',
        email: '{user_email}',
        role: 'user'
      }}
    }});

    expect(response.status()).toBe(201);
    const json = await response.json();
    const validated = UserSchema.parse(json);
    createdUserId = validated.id;
    expect(createdUserId).toBeTruthy();
  }});

  test('Tier 0: Create Item with strict Zod assertion', async ({{ request }}) => {{
    const response = await request.post(`${{BASE_URL}}/items`, {{
      headers: {{
        'Authorization': `Bearer ${{ADMIN_TOKEN}}`,
        'Content-Type': 'application/json'
      }},
      data: {{
        name: '{item_name}',
        sku: '{item_sku}',
        price: {item_price},
        category: '{item_category}'
      }}
    }});

    expect(response.status()).toBe(201);
    const json = await response.json();
    const validated = ItemSchema.parse(json);
    createdItemId = validated.id;
    expect(createdItemId).toBeTruthy();
  }});

  test('Tier 1: Create Order using state handoff IDs', async ({{ request }}) => {{
    // Pre-requisite fallback if isolated test runner
    if (!createdUserId) createdUserId = 'usr_synthetic';
    if (!createdItemId) createdItemId = 'item_synthetic';

    const response = await request.post(`${{BASE_URL}}/orders`, {{
      headers: {{
        'Authorization': `Bearer ${{USER_TOKEN}}`,
        'Content-Type': 'application/json'
      }},
      data: {{
        user_id: createdUserId,
        item_ids: [createdItemId],
        shipping_address: '100 Tech Way'
      }}
    }});

    expect(response.status()).toBe(201);
    const json = await response.json();
    const validated = OrderSchema.parse(json);
    createdOrderId = validated.id;
    expect(createdOrderId).toBeTruthy();
  }});

  // PILLAR 1: Unsupported Method Enforcement
  test('Pillar 1: Unsupported Method (PATCH on /users) returns 405 or 404', async ({{ request }}) => {{
    const response = await request.patch(`${{BASE_URL}}/users`, {{
      headers: {{ 'Authorization': `Bearer ${{USER_TOKEN}}` }}
    }});
    expect([405, 404]).toContain(response.status());
  }});

  // PILLAR 2: Routing Boundary Checks
  test('Pillar 2: Non-existent resource path returns 404', async ({{ request }}) => {{
    const response = await request.get(`${{BASE_URL}}/users/non_existent_id_99999`, {{
      headers: {{ 'Authorization': `Bearer ${{USER_TOKEN}}` }}
    }});
    expect(response.status()).toBe(404);
  }});

  // PILLAR 3: Auth & RBAC Checks
  test('Pillar 3: Missing authorization header returns 401 Unauthorized', async ({{ request }}) => {{
    const response = await request.get(`${{BASE_URL}}/users/usr_test`);
    expect(response.status()).toBe(401);
    expect(response.headers()['www-authenticate']).toBeDefined();
  }});

  test('Pillar 3: User token forbidden on Admin endpoint returns 403', async ({{ request }}) => {{
    const response = await request.delete(`${{BASE_URL}}/users/usr_test`, {{
      headers: {{ 'Authorization': `Bearer ${{USER_TOKEN}}` }}
    }});
    expect(response.status()).toBe(403);
  }});
}});
"""

        playwright_config = f"""import {{ defineConfig }} from '@playwright/test';

export default defineConfig({{
  testDir: './tests',
  timeout: 30000,
  use: {{
    baseURL: process.env.BASE_URL || '{self.base_url}',
    extraHTTPHeaders: {{
      'Accept': 'application/json',
    }},
  }},
  reporter: [['html', {{ outputFolder: 'playwright-report', open: 'never' }}]],
}});
"""

        package_json = """{
  "name": "api-factory-generated-tests",
  "version": "1.0.0",
  "scripts": {
    "test": "playwright test"
  },
  "devDependencies": {
    "@playwright/test": "^1.45.0",
    "typescript": "^5.0.0",
    "zod": "^3.23.0"
  }
}
"""

        return {
          "tests/api_regression.spec.ts": spec_content,
          "playwright.config.ts": playwright_config,
          "package.json": package_json
        }
