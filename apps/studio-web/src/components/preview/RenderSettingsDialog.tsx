"use client";

import { motion } from "framer-motion";
import { X } from "lucide-react";
import { useState } from "react";

interface RenderSettingsDialogProps {
  projectId: string;
  onClose: () => void;
}

export function RenderSettingsDialog({
  projectId,
  onClose,
}: RenderSettingsDialogProps) {
  const [settings, setSettings] = useState({
    resolution: "1080p",
    fps: 30,
    codec: "h264",
    bitrate: "5mbps",
    platform: null as string | null,
    qualityLevel: 85,
  });

  const platforms = [
    {
      name: "YouTube",
      value: "youtube",
      presets: { resolution: "1080p", fps: 60 },
    },
    {
      name: "Shorts",
      value: "shorts",
      presets: { resolution: "1080p", fps: 30 },
    },
    {
      name: "TikTok",
      value: "tiktok",
      presets: { resolution: "1080p", fps: 30 },
    },
    {
      name: "Instagram",
      value: "instagram",
      presets: { resolution: "1080p", fps: 30 },
    },
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
        className="bg-slate-900 border border-slate-800 rounded-xl w-full max-w-xl max-h-[80vh] overflow-y-auto"
      >
        {/* Header */}
        <div className="sticky top-0 h-14 border-b border-slate-800 bg-slate-900 px-6 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-white">Render Settings</h2>
          <button
            onClick={onClose}
            className="p-1 rounded hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Platform presets */}
          <div>
            <label className="block text-sm font-semibold text-slate-300 mb-3">
              Platform Presets
            </label>
            <div className="grid grid-cols-2 gap-2">
              {platforms.map((platform) => (
                <motion.button
                  key={platform.value}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() =>
                    setSettings({ ...settings, platform: platform.value })
                  }
                  className={`p-3 rounded-lg border transition-colors ${
                    settings.platform === platform.value
                      ? "border-blue-500 bg-blue-500/10 text-blue-300"
                      : "border-slate-700 bg-slate-800/50 text-slate-300 hover:border-slate-600"
                  }`}
                >
                  {platform.name}
                </motion.button>
              ))}
            </div>
          </div>

          {/* Resolution */}
          <div>
            <label className="block text-sm font-semibold text-slate-300 mb-2">
              Resolution
            </label>
            <select
              value={settings.resolution}
              onChange={(e) =>
                setSettings({ ...settings, resolution: e.target.value })
              }
              className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-white focus:outline-none focus:border-blue-500"
            >
              <option value="720p">720p</option>
              <option value="1080p">1080p</option>
              <option value="2k">2K</option>
              <option value="4k">4K</option>
            </select>
          </div>

          {/* FPS */}
          <div>
            <label className="block text-sm font-semibold text-slate-300 mb-2">
              Frame Rate
            </label>
            <select
              value={settings.fps}
              onChange={(e) =>
                setSettings({ ...settings, fps: parseInt(e.target.value) })
              }
              className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-white focus:outline-none focus:border-blue-500"
            >
              <option value={24}>24 FPS</option>
              <option value={30}>30 FPS</option>
              <option value={60}>60 FPS</option>
            </select>
          </div>

          {/* Codec */}
          <div>
            <label className="block text-sm font-semibold text-slate-300 mb-2">
              Video Codec
            </label>
            <select
              value={settings.codec}
              onChange={(e) =>
                setSettings({ ...settings, codec: e.target.value })
              }
              className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-white focus:outline-none focus:border-blue-500"
            >
              <option value="h264">H.264 (Universal)</option>
              <option value="h265">H.265 (Better compression)</option>
              <option value="av1">AV1 (Best compression)</option>
            </select>
          </div>

          {/* Bitrate */}
          <div>
            <label className="block text-sm font-semibold text-slate-300 mb-2">
              Video Bitrate
            </label>
            <select
              value={settings.bitrate}
              onChange={(e) =>
                setSettings({ ...settings, bitrate: e.target.value })
              }
              className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-white focus:outline-none focus:border-blue-500"
            >
              <option value="3mbps">3 Mbps (Low)</option>
              <option value="5mbps">5 Mbps (Medium)</option>
              <option value="8mbps">8 Mbps (High)</option>
              <option value="12mbps">12 Mbps (Very High)</option>
            </select>
          </div>

          {/* Quality slider */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="block text-sm font-semibold text-slate-300">
                Quality Level
              </label>
              <span className="text-sm font-semibold text-blue-400">
                {settings.qualityLevel}%
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={settings.qualityLevel}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  qualityLevel: parseInt(e.target.value),
                })
              }
              className="w-full"
            />
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
            onClick={onClose}
            className="flex-1 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-medium transition-colors"
          >
            Save Settings
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
}
