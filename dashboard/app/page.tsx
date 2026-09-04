'use client';

import React, { useState } from 'react';
import { FragilityHeatmap, Endpoint } from './components/FragilityHeatmap';
import { DAGCanvas, DAGTier, StateHandoff } from './components/DAGCanvas';
import { ZodStudio } from './components/ZodStudio';
import { SelfHealingAudit } from './components/SelfHealingAudit';

const INITIAL_ENDPOINTS: Endpoint[] = [
  {
    tool_name: 'create_user',
    description: 'Creates a new user in the system.',
    path: '/users',
    method: 'POST',
    auth_required: true,
    fragility_score: 15,
    fragility_reasons: [],
    excluded: false,
  },
  {
    tool_name: 'get_user',
    description: 'Retrieves user details by user ID.',
    path: '/users/{user_id}',
    method: 'GET',
    auth_required: true,
    fragility_score: 20,
    fragility_reasons: [],
    excluded: false,
  },
  {
    tool_name: 'create_item',
    description: 'Creates a new item inventory catalog record.',
    path: '/items',
    method: 'POST',
    auth_required: true,
    fragility_score: 75,
    fragility_reasons: ['Strict SKU regex pattern constraint: ^[A-Z]{3}-\\d{4}$', 'Requires admin privileges'],
    excluded: false,
  },
  {
    tool_name: 'create_order',
    description: 'Creates an order linking a user ID and list of item IDs.',
    path: '/orders',
    method: 'POST',
    auth_required: true,
    fragility_score: 60,
    fragility_reasons: ['Multi-entity foreign key dependency (user_id, item_ids)'],
    excluded: false,
  },
  {
    tool_name: 'delete_user',
    description: 'Deletes a user account.',
    path: '/users/{user_id}',
    method: 'DELETE',
    auth_required: true,
    fragility_score: 40,
    fragility_reasons: ['State destructive operation'],
    excluded: false,
  },
];

const INITIAL_TIERS: DAGTier[] = [
  { tier: 0, tools: ['create_user', 'create_item'] },
  { tier: 1, tools: ['create_order'] },
  { tier: 2, tools: ['get_user', 'get_item', 'get_order'] },
];

const INITIAL_HANDOFFS: StateHandoff[] = [
  { source_tool: 'create_user', source_field: 'id', target_tool: 'create_order', target_param: 'user_id' },
  { source_tool: 'create_item', source_field: 'id', target_tool: 'create_order', target_param: 'item_ids' },
];

const SAMPLE_PAYLOAD = `{
  "id": "item_9f2a81b2",
  "name": "Enterprise Server License",
  "sku": "WGD-1234",
  "price": 299.99,
  "category": "Software",
  "created_at": "2026-09-04T03:00:00Z"
}`;

const SAMPLE_ZOD_SCHEMA = `export const ItemSchema = z.object({
  id: z.string(),
  name: z.string(),
  sku: z.string().regex(/^[A-Z]{3}-\\d{4}$/),
  price: z.number().positive(),
  category: z.string(),
  created_at: z.string()
});`;

export default function Home() {
  const [endpoints, setEndpoints] = useState<Endpoint[]>(INITIAL_ENDPOINTS);

  const handleToggleExclude = (toolName: string) => {
    setEndpoints(prev =>
      prev.map(ep => (ep.tool_name === toolName ? { ...ep, excluded: !ep.excluded } : ep))
    );
  };

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 p-8 font-sans">
      <header className="max-w-7xl mx-auto mb-8 border-b border-slate-800 pb-6 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white flex items-center gap-3">
            <span className="p-2 bg-blue-600 rounded-lg text-xl">⚡</span>
            API Automation Factory
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Autonomous A2A Swarm for MCP Introspection, Dependency Graphing, and Playwright Testing
          </p>
        </div>
        <div className="flex gap-3">
          <span className="px-3 py-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded-full text-xs font-semibold">
            AWS Strands SDK Active
          </span>
          <span className="px-3 py-1 bg-purple-500/10 text-purple-400 border border-purple-500/30 rounded-full text-xs font-semibold">
            Bedrock Claude 3.5 Sonnet
          </span>
        </div>
      </header>

      <div className="max-w-7xl mx-auto space-y-8">
        <FragilityHeatmap endpoints={endpoints} onToggleExclude={handleToggleExclude} />

        <DAGCanvas tiers={INITIAL_TIERS} handoffs={INITIAL_HANDOFFS} teardownTools={['delete_order', 'delete_user']} />

        <ZodStudio samplePayload={SAMPLE_PAYLOAD} zodSchema={SAMPLE_ZOD_SCHEMA} />

        <SelfHealingAudit
          iterations={2}
          selfHealed={true}
          recommendations={[
            "Iteration 1: Test failed on POST /items with HTTP 422 Unprocessable Entity. Server required regex '^[A-Z]{3}-\\d{4}$'.",
            "Iteration 2: Agent 4 instructed Agent 3 to adjust fixture 'item_sku' to 'WGD-1234'. Re-run passed 100% of assertions."
          ]}
          failureLogs={[
            "HTTP 422 Unprocessable Entity on POST /items. Detail: Field 'sku' violates format constraint. Expected regex '^[A-Z]{3}-\\d{4}$', got 'SKU9999'"
          ]}
        />
      </div>
    </main>
  );
}
