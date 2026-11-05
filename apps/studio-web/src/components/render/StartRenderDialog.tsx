"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { X } from "lucide-react";

interface StartRenderDialogProps {
  onClose: () => void;
  onStart: (quality: string, platform?: string) => void;
}

export function StartRenderDialog({
  onClose,
  onStart,
}: StartRenderDialogProps) {
  const [quality, setQuality] = useState("standard");
  const [platform, setPlatform] = useState<string | undefined>();

  const qualityPresets = [
    {
      name: "Draft",
      value: "draft",
      description: "Fast preview rendering",
      time: "~5m",
      size: "~50MB",
    },
    {
      name: "Standard",
      value: "standard",
      description: "Balanced quality and speed",
      time: "~10m",
      size: "~100MB",
    },
    {
      name: "High",
      value: "high",
      description: "High quality render",
      time: "~20m",
      size: "~200MB",
    },
    {
      name: "Ultra",
      value: "ultra",
      description: "4K professional quality",
      time: "~60m",
      size: "~500MB",
    },
  ];

  const platformPresets = [
    { name: "YouTube", value: "youtube" },
    { name: "YouTube Shorts", value: "shorts" },
    { name: "TikTok", value: "tiktok" },
    { name: "Instagram", value: "instagram" },
    { name: "LinkedIn", value: "linkedin" },
    { name: "Podcast", value: "podcast" },
  ];

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        onClick={(e) => e.stopPropagation()}
        className="bg-slate-900 border border-slate-800 rounded-xl w-full max-w-lg max-h-[80vh] overflow-y-auto"
      >
        {/* Header */}
        <div className="sticky top-0 h-14 border-b border-slate-800 bg-slate-900 px-6 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-white">Start Render</h2>
          <button
            onClick={onClose}
            className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Quality presets */}
          <div>
            <label className="block text-sm font-semibold text-slate-300 mb-3">
              Quality Preset
            </label>
            <div className="grid grid-cols-2 gap-3">
              {qualityPresets.map((preset) => (
                <motion.button
                  key={preset.value}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => setQuality(preset.value)}
                  className={`p-3 rounded-lg border transition-all text-left ${
                    quality === preset.value
                      ? "border-blue-500 bg-blue-500/10"
                      : "border-slate-700 bg-slate-800/50 hover:border-slate-600"
                  }`}
                >
                  <div className="font-medium text-white">{preset.name}</div>
                  <div className="text-xs text-slate-400 mt-1">
                    {preset.description}
                  </div>
                  <div className="text-xs text-slate-500 mt-2">
                    {preset.time} • {preset.size}
                  </div>
                </motion.button>
              ))}
            </div>
          </div>

          {/* Platform presets */}
          <div>
            <label className="block text-sm font-semibold text-slate-300 mb-3">
              Platform (Optional)
            </label>
            <div className="grid grid-cols-2 gap-2">
              {platformPresets.map((p) => (
                <motion.button
                  key={p.value}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() =>
                    setPlatform(platform === p.value ? undefined : p.value)
                  }
                  className={`p-2.5 rounded-lg border transition-colors text-sm font-medium ${
                    platform === p.value
                      ? "border-green-500 bg-green-500/10 text-green-300"
                      : "border-slate-700 text-slate-300 hover:border-slate-600"
                  }`}
                >
                  {p.name}
                </motion.button>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 border-t border-slate-800 bg-slate-900 px-6 py-4 flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-medium transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={() => onStart(quality, platform)}
            className="flex-1 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-medium transition-colors"
          >
            Start Render
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
}
