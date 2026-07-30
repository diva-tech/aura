"use client";

import { motion } from "framer-motion";
import { Pause, Play, Trash2, RotateCcw } from "lucide-react";
import { RenderJobProgress } from "./RenderJobProgress";

interface RenderQueueProps {
  renders: any[];
  projectId: string;
}

export function RenderQueue({ renders, projectId }: RenderQueueProps) {
  const currentRender = renders.find(
    (r) => r.status === "rendering" || r.status === "queued"
  );
  const queuedRenders = renders.filter((r) => r.status === "queued");
  const failedRenders = renders.filter((r) => r.status === "failed");

  if (!renders.length) {
    return (
      <div className="text-center py-12 text-slate-400">
        <p className="mb-2">No renders in queue</p>
        <p className="text-sm">Start a render to see it here</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Current render */}
      {currentRender && (
        <div>
          <h2 className="text-sm font-semibold text-slate-300 mb-3 uppercase">
            Currently Rendering
          </h2>
          <RenderJobProgress render={currentRender} isCurrent />
        </div>
      )}

      {/* Queued renders */}
      {queuedRenders.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold text-slate-300 mb-3 uppercase">
            Queue ({queuedRenders.length})
          </h2>
          <div className="space-y-2">
            {queuedRenders.map((render) => (
              <RenderJobProgress key={render.id} render={render} />
            ))}
          </div>
        </div>
      )}

      {/* Failed renders */}
      {failedRenders.length > 0 && (
        <div>
          <h2 className="text-sm font-semibold text-red-400 mb-3 uppercase">
            Failed ({failedRenders.length})
          </h2>
          <div className="space-y-2">
            {failedRenders.map((render) => (
              <motion.div
                key={render.id}
                className="p-4 rounded-lg border border-red-700/50 bg-red-900/20"
              >
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <span className="text-sm font-medium text-white">
                      Render v{render.version || 1}
                    </span>
                    <p className="text-xs text-red-300 mt-1">
                      {render.error_message}
                    </p>
                  </div>
                  <div className="flex gap-1">
                    <button className="p-2 rounded hover:bg-red-800/30 text-red-400 hover:text-red-300 transition-colors">
                      <RotateCcw size={16} />
                    </button>
                    <button className="p-2 rounded hover:bg-red-800/30 text-red-400 hover:text-red-300 transition-colors">
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
