"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { usePreview, useRenderEstimate } from "@/lib/api/preview";
import { ComparisonView } from "./ComparisonView";
import { RenderEstimatePanel } from "./RenderEstimatePanel";
import { RenderSettingsDialog } from "./RenderSettingsDialog";
import { PreviewValidation } from "./PreviewValidation";
import { PreviewComments } from "./PreviewComments";

interface PreviewLayoutProps {
  projectId: string;
}

export function PreviewLayout({ projectId }: PreviewLayoutProps) {
  const { data: preview, isLoading } = usePreview(projectId);
  const { data: estimate } = useRenderEstimate(projectId);
  const [showSettings, setShowSettings] = useState(false);
  const [showComments, setShowComments] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);

  if (isLoading) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="h-screen flex items-center justify-center bg-slate-950"
      >
        <div className="text-center">
          <div className="mb-4 text-slate-400">Generating preview...</div>
          <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto" />
        </div>
      </motion.div>
    );
  }

  if (!preview) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="h-screen flex items-center justify-center bg-slate-950"
      >
        <div className="text-center">
          <div className="text-slate-300 mb-4">No preview generated</div>
          <p className="text-slate-500 text-sm">
            Approve your edit plan to generate a preview
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
          <h1 className="text-xl font-semibold">Preview & Render</h1>
          <p className="text-xs text-slate-500">
            Version {preview.version} • {preview.status}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowComments(!showComments)}
            className="px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-sm font-medium transition-colors"
          >
            Comments
          </button>
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="px-3 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-sm font-medium transition-colors"
          >
            Settings
          </button>
          <button className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-sm font-medium transition-colors disabled:opacity-50">
            {preview.approved ? "✓ Approved" : "Approve Preview"}
          </button>
        </div>
      </motion.div>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Comparison view */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex-1 border-r border-slate-800 overflow-hidden"
        >
          <ComparisonView
            projectId={projectId}
            currentTime={currentTime}
            onTimeChange={setCurrentTime}
          />
        </motion.div>

        {/* Right panel: Settings + Estimate + Validation */}
        <motion.div
          initial={{ x: 400, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="w-96 border-l border-slate-800 flex flex-col overflow-hidden"
        >
          {showComments ? (
            <PreviewComments previewId={preview.id} />
          ) : (
            <>
              <RenderEstimatePanel estimate={estimate} />
              <PreviewValidation previewId={preview.id} />
            </>
          )}
        </motion.div>
      </div>

      {/* Settings dialog */}
      {showSettings && (
        <RenderSettingsDialog
          projectId={projectId}
          onClose={() => setShowSettings(false)}
        />
      )}
    </div>
  );
}
