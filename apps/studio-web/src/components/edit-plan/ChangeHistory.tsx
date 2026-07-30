"use client";

import { motion } from "framer-motion";
import { RotateCcw, FileText } from "lucide-react";

interface ChangeHistoryProps {
  editPlanId: string;
}

export function ChangeHistory({ editPlanId }: ChangeHistoryProps) {
  const mockHistory = [
    {
      id: "1",
      version: 3,
      changeType: "manual_edit",
      description: "Moved intro cut to 0:05",
      timestamp: new Date(),
    },
    {
      id: "2",
      version: 2,
      changeType: "ai_regenerate",
      description: 'Regenerated with "make it more cinematic"',
      timestamp: new Date(Date.now() - 60000),
    },
    {
      id: "3",
      version: 1,
      changeType: "ai_generate",
      description: "Initial edit plan generated",
      timestamp: new Date(Date.now() - 120000),
    },
  ];

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <div className="px-4 py-3 border-b border-slate-800">
        <h3 className="text-sm font-semibold text-slate-300">Change History</h3>
        <p className="text-xs text-slate-500 mt-1">
          {mockHistory.length} changes
        </p>
      </div>

      <div className="flex-1 overflow-y-auto">
        <div className="space-y-2 p-4">
          {mockHistory.map((change, idx) => (
            <motion.div
              key={change.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.05 }}
              className="p-3 rounded-lg border border-slate-700 hover:border-slate-600 bg-slate-800/30 group"
            >
              <div className="flex items-start gap-3">
                <div className="mt-0.5">
                  {change.changeType === "ai_regenerate" && (
                    <FileText size={16} className="text-blue-400" />
                  )}
                  {change.changeType === "manual_edit" && (
                    <RotateCcw size={16} className="text-green-400" />
                  )}
                  {change.changeType === "ai_generate" && (
                    <FileText size={16} className="text-purple-400" />
                  )}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-sm font-medium text-white truncate">
                      v{change.version}
                    </span>
                    <span className="text-xs text-slate-500 whitespace-nowrap">
                      {formatTime(change.timestamp)}
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 mt-1 line-clamp-2">
                    {change.description}
                  </p>
                </div>
              </div>

              <button className="w-full mt-2 px-2 py-1.5 rounded bg-slate-700/50 hover:bg-slate-700 text-white text-xs font-medium transition-colors opacity-0 group-hover:opacity-100">
                Restore
              </button>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}

function formatTime(date: Date): string {
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (minutes < 1) return "Just now";
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  return `${days}d ago`;
}
