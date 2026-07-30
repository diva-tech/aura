"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { useListRenders, useStartRender } from "@/lib/api/render";
import { RenderQueue } from "./RenderQueue";
import { DownloadCenter } from "./DownloadCenter";
import { GPUMonitoring } from "./GPUMonitoring";
import { StartRenderDialog } from "./StartRenderDialog";

interface RenderQueueLayoutProps {
  projectId: string;
}

export function RenderQueueLayout({ projectId }: RenderQueueLayoutProps) {
  const { data: renders } = useListRenders({ projectId });
  const [showStartDialog, setShowStartDialog] = useState(false);
  const [activeTab, setActiveTab] = useState<"queue" | "history" | "download">(
    "queue"
  );

  const renderMutation = useStartRender();

  const currentRender = renders?.find(
    (r) => r.status === "rendering" || r.status === "queued"
  );
  const completedRenders =
    renders?.filter((r) => r.status === "completed") || [];
  const failedRenders = renders?.filter((r) => r.status === "failed") || [];

  const handleStartRender = async (quality: string, platform?: string) => {
    try {
      await renderMutation.mutateAsync({ projectId, quality, platform });
      setShowStartDialog(false);
    } catch (error) {
      console.error("Failed to start render:", error);
    }
  };

  return (
    <div className="h-screen flex flex-col bg-slate-950 text-white">
      {/* Header */}
      <motion.div
        initial={{ y: -60, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="h-16 border-b border-slate-800 bg-gradient-to-r from-slate-900 to-slate-800/50 flex items-center justify-between px-8"
      >
        <div>
          <h1 className="text-xl font-semibold">Render Queue</h1>
          <p className="text-xs text-slate-500">
            {currentRender ? "Rendering in progress" : "Ready to render"}
          </p>
        </div>

        <button
          onClick={() => setShowStartDialog(true)}
          className="px-6 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-sm font-medium transition-colors"
        >
          Start Render
        </button>
      </motion.div>

      {/* Tabs */}
      <div className="border-b border-slate-800 bg-slate-900/50 px-8 flex gap-6">
        {(["queue", "history", "download"] as const).map((tab) => (
          <motion.button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`py-4 text-sm font-medium border-b-2 transition-colors ${
              activeTab === tab
                ? "border-blue-600 text-white"
                : "border-transparent text-slate-400 hover:text-slate-300"
            }`}
          >
            {tab === "queue" && `Queue (${renders?.length || 0})`}
            {tab === "history" && `History (${completedRenders.length})`}
            {tab === "download" && "Download Center"}
          </motion.button>
        ))}
      </div>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left panel */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex-1 border-r border-slate-800 p-6 overflow-y-auto"
        >
          {activeTab === "queue" && (
            <RenderQueue renders={renders || []} projectId={projectId} />
          )}
          {activeTab === "history" && (
            <div className="space-y-3">
              {completedRenders.map((render) => (
                <RenderJobCard key={render.id} render={render} />
              ))}
              {completedRenders.length === 0 && (
                <div className="text-center py-12 text-slate-400">
                  No completed renders yet
                </div>
              )}
            </div>
          )}
          {activeTab === "download" && (
            <DownloadCenter renders={completedRenders} />
          )}
        </motion.div>

        {/* Right panel: GPU Monitoring */}
        <motion.div
          initial={{ x: 400, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="w-80 border-l border-slate-800 p-6 overflow-y-auto"
        >
          <GPUMonitoring currentRender={currentRender} />
        </motion.div>
      </div>

      {/* Start render dialog */}
      {showStartDialog && (
        <StartRenderDialog
          onClose={() => setShowStartDialog(false)}
          onStart={handleStartRender}
        />
      )}
    </div>
  );
}

function RenderJobCard({ render }: { render: any }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="p-4 rounded-lg border border-slate-700 bg-slate-800/30 hover:border-slate-600 transition-colors"
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-white truncate">
          Render v{render.version || 1}
        </span>
        <span className="text-xs px-2 py-1 rounded-full bg-green-900/30 text-green-300">
          {render.status}
        </span>
      </div>
      <div className="text-xs text-slate-400">
        {render.quality} • {render.resolution} • {render.codec}
      </div>
    </motion.div>
  );
}
