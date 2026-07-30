"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { useListPublishJobs } from "@/lib/api/publish";
import { PlatformSelector } from "./PlatformSelector";
import { PublishQueueView } from "./PublishQueueView";
import { PublishHistoryView } from "./PublishHistoryView";
import { PlatformHealthDashboard } from "./PlatformHealthDashboard";
import { PublishMetadataForm } from "./PublishMetadataForm";

interface PublishingHubProps {
  projectId: string;
}

export function PublishingHub({ projectId }: PublishingHubProps) {
  const { data: publishJobs } = useListPublishJobs({ projectId });
  const [activeTab, setActiveTab] = useState<"publish" | "queue" | "history">(
    "publish"
  );
  const [selectedPlatform, setSelectedPlatform] = useState<string | null>(null);
  const [showMetadataForm, setShowMetadataForm] = useState(false);

  const queuedJobs = publishJobs?.filter((j) => j.status === "queued") || [];
  const publishedJobs =
    publishJobs?.filter((j) => j.status === "published") || [];
  const failedJobs = publishJobs?.filter((j) => j.status === "failed") || [];

  return (
    <div className="h-screen flex flex-col bg-slate-950 text-white">
      {/* Header */}
      <motion.div
        initial={{ y: -60, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="h-16 border-b border-slate-800 bg-gradient-to-r from-slate-900 to-slate-800/50 flex items-center justify-between px-8"
      >
        <div>
          <h1 className="text-xl font-semibold">Publishing Hub</h1>
          <p className="text-xs text-slate-500">
            {queuedJobs.length} queued • {publishedJobs.length} published
          </p>
        </div>
      </motion.div>

      {/* Tabs */}
      <div className="border-b border-slate-800 bg-slate-900/50 px-8 flex gap-6">
        {(["publish", "queue", "history"] as const).map((tab) => (
          <motion.button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`py-4 text-sm font-medium border-b-2 transition-colors ${
              activeTab === tab
                ? "border-blue-600 text-white"
                : "border-transparent text-slate-400 hover:text-slate-300"
            }`}
          >
            {tab === "publish" && "Publish"}
            {tab === "queue" && `Queue (${queuedJobs.length})`}
            {tab === "history" && `History (${publishedJobs.length})`}
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
          {activeTab === "publish" && (
            <div className="space-y-6">
              <PlatformSelector
                onSelectPlatform={(platform) => {
                  setSelectedPlatform(platform);
                  setShowMetadataForm(true);
                }}
              />
              {showMetadataForm && selectedPlatform && (
                <PublishMetadataForm
                  platform={selectedPlatform}
                  projectId={projectId}
                  onClose={() => {
                    setShowMetadataForm(false);
                    setSelectedPlatform(null);
                  }}
                />
              )}
            </div>
          )}
          {activeTab === "queue" && <PublishQueueView jobs={queuedJobs} />}
          {activeTab === "history" && (
            <PublishHistoryView
              publishedJobs={publishedJobs}
              failedJobs={failedJobs}
            />
          )}
        </motion.div>

        {/* Right panel: Platform Health */}
        <motion.div
          initial={{ x: 400, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="w-80 border-l border-slate-800 p-6 overflow-y-auto"
        >
          <PlatformHealthDashboard />
        </motion.div>
      </div>
    </div>
  );
}
