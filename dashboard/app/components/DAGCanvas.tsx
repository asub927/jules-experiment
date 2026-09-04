'use client';

import React from 'react';

export interface DAGTier {
  tier: number;
  tools: string[];
}

export interface StateHandoff {
  source_tool: string;
  source_field: string;
  target_tool: string;
  target_param: string;
}

interface DAGCanvasProps {
  tiers: DAGTier[];
  handoffs: StateHandoff[];
  teardownTools: string[];
}

export function DAGCanvas({ tiers, handoffs, teardownTools }: DAGCanvasProps) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 text-slate-100 shadow-xl mt-6">
      <div className="mb-6">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-blue-500 inline-block animate-pulse"></span>
          Checkpoint 2: Interactive Dependency DAG Canvas
        </h2>
        <p className="text-sm text-slate-400">
          Inferred CRUD execution tiers, foreign key state harvesting, and teardown order.
        </p>
      </div>

      <div className="flex flex-col gap-6">
        {tiers.map((tier, idx) => (
          <div key={idx} className="relative bg-slate-950/60 border border-slate-800 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-2">
              <span className="text-xs font-bold text-blue-400 tracking-wider uppercase">
                Tier {tier.tier}: {tier.tier === 0 ? 'Root Entities (Independent)' : tier.tier === 1 ? 'Dependent Entities (Foreign Keys)' : 'Read & Query Operations'}
              </span>
              <span className="text-xs text-slate-500 font-mono">{tier.tools.length} Tools</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {tier.tools.map(tool => {
                const incomingHandoffs = handoffs.filter(h => h.target_tool === tool);
                return (
                  <div key={tool} className="bg-slate-800/80 border border-slate-700 rounded-lg p-3 hover:border-blue-500 transition">
                    <div className="font-mono text-sm font-semibold text-slate-200">{tool}</div>
                    {incomingHandoffs.length > 0 && (
                      <div className="mt-2 pt-2 border-t border-slate-700/60">
                        <span className="text-[10px] text-amber-400 font-bold uppercase tracking-wider block">State Handoffs Received:</span>
                        {incomingHandoffs.map((h, i) => (
                          <div key={i} className="text-xs text-slate-300 font-mono mt-1 bg-slate-900/80 p-1.5 rounded border border-slate-800">
                            <span className="text-emerald-400">{h.source_tool}</span>.{h.source_field} &rarr; <span className="text-blue-400">{h.target_param}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        ))}

        {teardownTools.length > 0 && (
          <div className="bg-rose-950/20 border border-rose-900/40 rounded-lg p-4">
            <div className="text-xs font-bold text-rose-400 uppercase tracking-wider mb-2">
              Teardown & Cleanup Hooks (Post-Execution)
            </div>
            <div className="flex flex-wrap gap-2">
              {teardownTools.map(t => (
                <span key={t} className="px-3 py-1 bg-rose-900/30 text-rose-300 text-xs font-mono font-medium rounded border border-rose-800">
                  {t}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
