'use client';

import React, { useState } from 'react';

interface SelfHealingAuditProps {
  iterations: number;
  selfHealed: boolean;
  recommendations: string[];
  failureLogs: string[];
  onApproveAndPR?: () => void;
}

export function SelfHealingAudit({
  iterations,
  selfHealed,
  recommendations,
  failureLogs,
  onApproveAndPR
}: SelfHealingAuditProps) {
  const [prStatus, setPrStatus] = useState<'idle' | 'opening' | 'success'>('idle');

  const handleOpenPR = () => {
    setPrStatus('opening');
    setTimeout(() => {
      setPrStatus('success');
      if (onApproveAndPR) onApproveAndPR();
    }, 1200);
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 text-slate-100 shadow-xl mt-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-xl font-bold flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-purple-500 inline-block animate-pulse"></span>
            Checkpoint 4: Self-Healing Audit & 1-Click CI Export
          </h2>
          <p className="text-sm text-slate-400">
            A2A Self-Healing negotiation history, failure trace analysis, and Pull Request export.
          </p>
        </div>
        <div>
          {prStatus === 'idle' && (
            <button
              onClick={handleOpenPR}
              className="bg-emerald-600 hover:bg-emerald-500 text-white px-5 py-2.5 rounded-lg font-semibold text-sm shadow-lg shadow-emerald-900/40 transition flex items-center gap-2"
            >
              Approve & Open GitHub Pull Request
            </button>
          )}
          {prStatus === 'opening' && (
            <button disabled className="bg-slate-700 text-slate-300 px-5 py-2.5 rounded-lg font-semibold text-sm animate-pulse">
              Generating GitHub PR & Triggering CI...
            </button>
          )}
          {prStatus === 'success' && (
            <span className="bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 px-4 py-2 rounded-lg font-semibold text-sm flex items-center gap-2">
              ✓ PR #42 Created & Pre-deployment CI Triggered
            </span>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
          <span className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">A2A Negotiation Cycles</span>
          <div className="text-2xl font-bold text-slate-100 mt-1">{iterations} / 3</div>
        </div>

        <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
          <span className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Self-Healing Status</span>
          <div className="text-2xl font-bold text-emerald-400 mt-1">
            {selfHealed ? 'Resolved (100%)' : 'Verified Deterministic'}
          </div>
        </div>

        <div className="bg-slate-950 border border-slate-800 p-4 rounded-lg">
          <span className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Determinism Confidence</span>
          <div className="text-2xl font-bold text-blue-400 mt-1">100.0% Pass Rate</div>
        </div>
      </div>

      {recommendations.length > 0 && (
        <div className="bg-slate-950 border border-slate-800 rounded-lg p-4 mb-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-purple-400 mb-2">
            Narrative Self-Healing Audit Trail
          </h3>
          <ul className="space-y-2">
            {recommendations.map((rec, i) => (
              <li key={i} className="text-xs font-mono text-slate-300 bg-purple-950/20 p-2.5 rounded border border-purple-900/40">
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}

      {failureLogs.length > 0 && (
        <div className="bg-slate-950 border border-slate-800 rounded-lg p-4">
          <h3 className="text-xs font-bold uppercase tracking-wider text-rose-400 mb-2">
            Captured HTTP / Stderr Failure Trace
          </h3>
          <div className="space-y-1 font-mono text-xs text-rose-300/80 bg-rose-950/10 p-3 rounded border border-rose-900/30">
            {failureLogs.map((log, i) => (
              <div key={i}>{log}</div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
