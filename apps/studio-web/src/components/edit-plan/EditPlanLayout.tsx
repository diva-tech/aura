"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { useEditPlan } from "@/lib/api/edit-plan";
import { VideoPlayer } from "./VideoPlayer";
import { InteractiveTimeline } from "./InteractiveTimeline";
import { EditPlanPanel } from "./EditPlanPanel";
import { HistoryPanel } from "./HistoryPanel";
import { ChangeHistory } from "./ChangeHistory";

interface EditPlanLayoutProps {
  projectId: string;
}

export function EditPlanLayout({ projectId }: EditPlanLayoutProps) {
  const { data: editPlan, isLoading } = useEditPlan(projectId);
  const [selectedClipId, setSelectedClipId] = useState<string | null>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [showHistory, setShowHistory] = useState(false);
  const [zoom, setZoom] = useState(100);

  if (isLoading) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="h-screen flex items-center justify-center bg-slate-950"
      >
        <div className="text-center">
          <div className="mb-4 text-slate-400">Loading edit plan...</div>
          <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto" />
        </div>
      </motion.div>
    );
  }

  if (!editPlan) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="h-screen flex items-center justify-center bg-slate-950"
      >
        <div className="text-center">
          <div className="text-slate-300 mb-4">No edit plan found</div>
          <p className="text-slate-500 text-sm">
            Accept suggestions to generate an edit plan
          </p>
        </div>
      </motion.div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-slate-950 text-white">
      {/* Header */}
      <motion.div
        initial={{ y: -60, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="h-16 border-b border-slate-800 bg-gradient-to-r from-slate-900 to-slate-800/50 flex items-center justify-between px-8"
      >
        <div>
          <h1 className="text-xl font-semibold">Edit Plan</h1>
          <p className="text-xs text-slate-500">
            Version {editPlan.version} • {editPlan.operations?.length || 0}{" "}
            operations
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-sm font-medium transition-colors"
          >
            History
          </button>
          <button className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-sm font-medium transition-colors disabled:opacity-50">
            Approve Plan
          </button>
        </div>
      </motion.div>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left panel: Video player */}
        <motion.div
          initial={{ x: -400, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          className="w-1/3 border-r border-slate-800 p-4 overflow-y-auto"
        >
          <VideoPlayer projectId={projectId} currentTime={currentTime} />
        </motion.div>

        {/* Center panel: Timeline */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="flex-1 border-r border-slate-800 p-4 overflow-hidden flex flex-col"
        >
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-slate-300">Timeline</h2>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setZoom(Math.max(50, zoom - 10))}
                className="px-2 py-1 text-xs rounded bg-slate-800 hover:bg-slate-700"
              >
                −
              </button>
              <span className="text-xs text-slate-400 min-w-[40px] text-center">
                {zoom}%
              </span>
              <button
                onClick={() => setZoom(Math.min(200, zoom + 10))}
                className="px-2 py-1 text-xs rounded bg-slate-800 hover:bg-slate-700"
              >
                +
              </button>
            </div>
          </div>
          <InteractiveTimeline
            editPlan={editPlan}
            selectedClipId={selectedClipId}
            onSelectClip={setSelectedClipId}
            currentTime={currentTime}
            onTimeChange={setCurrentTime}
            zoom={zoom}
          />
        </motion.div>

        {/* Right panel: Operations panel + History */}
        <motion.div
          initial={{ x: 400, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="w-80 border-l border-slate-800 flex flex-col overflow-hidden"
        >
          {showHistory ? (
            <ChangeHistory editPlanId={editPlan.id} />
          ) : (
            <EditPlanPanel
              editPlan={editPlan}
              selectedClipId={selectedClipId}
              onSelectOperation={(opId) => {
                // Find and select associated clip
              }}
            />
          )}
        </motion.div>
      </div>
    </div>
  );
}
