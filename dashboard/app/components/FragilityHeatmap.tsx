'use client';

import React, { useState } from 'react';

export interface Endpoint {
  tool_name: string;
  description: string;
  path: string;
  method: string;
  auth_required: boolean;
  fragility_score: number;
  fragility_reasons: string[];
  excluded: boolean;
}

interface FragilityHeatmapProps {
  endpoints: Endpoint[];
  onToggleExclude: (toolName: string) => void;
}

export function FragilityHeatmap({ endpoints, onToggleExclude }: FragilityHeatmapProps) {
  const [filter, setFilter] = useState<'all' | 'high_risk'>('all');

  const filtered = endpoints.filter(ep => {
    if (filter === 'high_risk') return ep.fragility_score >= 50;
    return true;
  });

  const getBadgeColor = (score: number) => {
    if (score >= 70) return 'bg-red-500/20 text-red-400 border-red-500/30';
    if (score >= 40) return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
    return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 text-slate-100 shadow-xl">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-xl font-bold flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-amber-500 inline-block animate-pulse"></span>
            Checkpoint 1: Introspection & Fragility Heatmap
          </h2>
          <p className="text-sm text-slate-400">
            Automated risk scoring based on schema complexity, missing auth, and route parameters.
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-3 py-1.5 text-xs font-semibold rounded-lg border transition ${
              filter === 'all'
                ? 'bg-blue-600 border-blue-500 text-white'
                : 'bg-slate-800 border-slate-700 text-slate-300 hover:bg-slate-700'
            }`}
          >
            All Endpoints ({endpoints.length})
          </button>
          <button
            onClick={() => setFilter('high_risk')}
            className={`px-3 py-1.5 text-xs font-semibold rounded-lg border transition ${
              filter === 'high_risk'
                ? 'bg-red-600 border-red-500 text-white'
                : 'bg-slate-800 border-slate-700 text-slate-300 hover:bg-slate-700'
            }`}
          >
            High Fragility (≥50)
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {filtered.map(ep => (
          <div
            key={ep.tool_name}
            className={`p-4 rounded-lg border transition ${
              ep.excluded
                ? 'bg-slate-950/50 border-slate-800 opacity-50'
                : 'bg-slate-800/50 border-slate-700 hover:border-slate-600'
            }`}
          >
            <div className="flex justify-between items-start mb-2">
              <div className="flex items-center gap-2">
                <span className={`px-2 py-0.5 text-xs font-mono font-bold rounded ${
                  ep.method === 'GET' ? 'bg-blue-500/20 text-blue-400' :
                  ep.method === 'POST' ? 'bg-emerald-500/20 text-emerald-400' :
                  ep.method === 'DELETE' ? 'bg-rose-500/20 text-rose-400' : 'bg-slate-700 text-slate-300'
                }`}>
                  {ep.method}
                </span>
                <span className="font-mono text-sm font-semibold">{ep.path}</span>
              </div>
              <span className={`px-2 py-0.5 text-xs font-bold rounded border ${getBadgeColor(ep.fragility_score)}`}>
                Fragility {ep.fragility_score}/100
              </span>
            </div>

            <p className="text-xs text-slate-400 mb-3">{ep.description}</p>

            {ep.fragility_reasons.length > 0 && (
              <div className="mb-3">
                <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Risk Factors</span>
                <ul className="text-xs text-amber-300/80 list-disc list-inside mt-1 space-y-0.5">
                  {ep.fragility_reasons.map((r, i) => (
                    <li key={i}>{r}</li>
                  ))}
                </ul>
              </div>
            )}

            <div className="flex justify-between items-center pt-2 border-t border-slate-700/50">
              <span className="text-xs text-slate-400 font-mono">
                Tool: <span className="text-slate-200">{ep.tool_name}</span>
              </span>
              <button
                onClick={() => onToggleExclude(ep.tool_name)}
                className={`px-2.5 py-1 text-xs font-medium rounded transition ${
                  ep.excluded
                    ? 'bg-emerald-600/20 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-600/30'
                    : 'bg-slate-700/50 text-slate-300 hover:bg-slate-700 border border-slate-600'
                }`}
              >
                {ep.excluded ? 'Include in Suite' : 'Exclude'}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
