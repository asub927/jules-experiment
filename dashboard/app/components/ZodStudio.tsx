'use client';

import React, { useState } from 'react';

interface ZodStudioProps {
  samplePayload: string;
  zodSchema: string;
  onUpdateSchema?: (newSchema: string) => void;
}

export function ZodStudio({ samplePayload, zodSchema }: ZodStudioProps) {
  const [strictChecking, setStrictChecking] = useState(true);
  const [currentSchema, setCurrentSchema] = useState(zodSchema);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 text-slate-100 shadow-xl mt-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-xl font-bold flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-emerald-500 inline-block animate-pulse"></span>
            Checkpoint 3: Zod Contract Studio
          </h2>
          <p className="text-sm text-slate-400">
            Side-by-side payload inspection & synthesized runtime Zod schema controls.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 text-xs font-semibold text-slate-300 cursor-pointer bg-slate-800 px-3 py-1.5 rounded-lg border border-slate-700">
            <input
              type="checkbox"
              checked={strictChecking}
              onChange={(e) => setStrictChecking(e.target.checked)}
              className="rounded bg-slate-900 border-slate-700 text-emerald-500 focus:ring-emerald-500"
            />
            Enforce .strict() (Fail on unexpected keys)
          </label>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Real-time Response Payload */}
        <div className="bg-slate-950 border border-slate-800 rounded-lg p-4 font-mono text-xs">
          <div className="flex justify-between items-center mb-3 pb-2 border-b border-slate-800">
            <span className="text-slate-400 font-sans font-bold uppercase tracking-wider text-[10px]">
              Target Endpoint Live Response
            </span>
            <span className="text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded text-[10px] font-bold">
              201 CREATED
            </span>
          </div>
          <pre className="text-emerald-300/90 overflow-x-auto whitespace-pre-wrap">{samplePayload}</pre>
        </div>

        {/* Synthesized Zod Schema */}
        <div className="bg-slate-950 border border-slate-800 rounded-lg p-4 font-mono text-xs">
          <div className="flex justify-between items-center mb-3 pb-2 border-b border-slate-800">
            <span className="text-slate-400 font-sans font-bold uppercase tracking-wider text-[10px]">
              Synthesized Zod Runtime Schema
            </span>
            <span className="text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded text-[10px] font-bold">
              TYPE-SAFE
            </span>
          </div>
          <textarea
            value={strictChecking && !currentSchema.includes('.strict()') ? currentSchema + '.strict()' : currentSchema}
            onChange={(e) => setCurrentSchema(e.target.value)}
            rows={12}
            className="w-full bg-transparent text-blue-300/90 focus:outline-none resize-none font-mono text-xs"
          />
        </div>
      </div>
    </div>
  );
}
