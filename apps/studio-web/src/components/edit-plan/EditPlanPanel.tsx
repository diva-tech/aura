"use client";

import { motion } from "framer-motion";
import { ChevronDown, Check, Trash2, Copy } from "lucide-react";
import { useState } from "react";

interface EditPlanPanelProps {
  editPlan: any;
  selectedClipId: string | null;
  onSelectOperation: (opId: string) => void;
}

export function EditPlanPanel({
  editPlan,
  selectedClipId,
  onSelectOperation,
}: EditPlanPanelProps) {
  const [expandedOps, setExpandedOps] = useState<Set<string>>(new Set());

  const toggleExpand = (opId: string) => {
    const newExpanded = new Set(expandedOps);
    if (newExpanded.has(opId)) {
      newExpanded.delete(opId);
    } else {
      newExpanded.add(opId);
    }
    setExpandedOps(newExpanded);
  };

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <div className="px-4 py-3 border-b border-slate-800">
        <h3 className="text-sm font-semibold text-slate-300">Operations</h3>
        <p className="text-xs text-slate-500 mt-1">
          {editPlan?.operations?.length || 0} edits to apply
        </p>
      </div>

      <div className="flex-1 overflow-y-auto">
        <div className="space-y-2 p-4">
          {editPlan?.operations?.map((op: any, idx: number) => (
            <motion.button
              key={op.id}
              layout
              onClick={() => toggleExpand(op.id)}
              className={`w-full text-left p-3 rounded-lg border transition-all ${
                expandedOps.has(op.id)
                  ? "border-blue-500 bg-blue-500/10"
                  : "border-slate-700 hover:border-slate-600 bg-slate-800/30"
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <Check size={14} className="text-green-400" />
                    <span className="text-sm font-medium text-white">
                      {op.title}
                    </span>
                  </div>
                  <div className="text-xs text-slate-400">
                    {op.start_time}ms → {op.end_time}ms
                  </div>
                </div>
                <ChevronDown
                  size={16}
                  className={`text-slate-500 transition-transform ${
                    expandedOps.has(op.id) ? "rotate-180" : ""
                  }`}
                />
              </div>

              {expandedOps.has(op.id) && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  className="mt-3 pt-3 border-t border-slate-700 text-xs space-y-2"
                >
                  <p className="text-slate-300">{op.description}</p>
                  <div className="bg-slate-900/50 p-2 rounded text-slate-400">
                    <p className="font-medium text-xs mb-1">Why:</p>
                    <p>{op.reason}</p>
                  </div>
                  <div className="flex gap-2">
                    <button className="flex-1 px-2 py-1.5 rounded bg-slate-700 hover:bg-slate-600 text-white font-medium transition-colors flex items-center justify-center gap-1">
                      <Copy size={12} />
                      Duplicate
                    </button>
                    <button className="flex-1 px-2 py-1.5 rounded bg-red-900/30 hover:bg-red-900/50 text-red-300 font-medium transition-colors">
                      Remove
                    </button>
                  </div>
                </motion.div>
              )}
            </motion.button>
          ))}
        </div>
      </div>
    </div>
  );
}
