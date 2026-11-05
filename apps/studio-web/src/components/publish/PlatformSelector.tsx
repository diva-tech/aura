"use client";

import { motion } from "framer-motion";
import {
  Youtube,
  Instagram,
  TrendingUp,
  Linkedin,
  Podcast,
  Plus,
} from "lucide-react";

interface PlatformSelectorProps {
  onSelectPlatform: (platform: string) => void;
}

const PLATFORMS = [
  {
    id: "youtube",
    name: "YouTube",
    icon: Youtube,
    description: "Full-length videos",
    color: "from-red-600 to-red-700",
  },
  {
    id: "shorts",
    name: "YouTube Shorts",
    icon: Youtube,
    description: "Short-form videos",
    color: "from-red-600 to-red-700",
  },
  {
    id: "instagram",
    name: "Instagram Reels",
    icon: Instagram,
    description: "Reels & Stories",
    color: "from-pink-600 to-purple-600",
  },
  {
    id: "tiktok",
    name: "TikTok",
    icon: TrendingUp,
    description: "Short-form videos",
    color: "from-black to-slate-800",
  },
  {
    id: "linkedin",
    name: "LinkedIn",
    icon: Linkedin,
    description: "Professional content",
    color: "from-blue-600 to-blue-700",
  },
  {
    id: "podcast",
    name: "Podcast",
    icon: Podcast,
    description: "Audio distribution",
    color: "from-purple-600 to-purple-700",
  },
];

export function PlatformSelector({ onSelectPlatform }: PlatformSelectorProps) {
  return (
    <div>
      <h2 className="text-lg font-semibold text-white mb-4">
        Select Platform to Publish
      </h2>
      <div className="grid grid-cols-2 gap-3">
        {PLATFORMS.map((platform) => {
          const Icon = platform.icon;
          return (
            <motion.button
              key={platform.id}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onSelectPlatform(platform.id)}
              className={`p-4 rounded-lg border border-slate-700 bg-gradient-to-br ${platform.color} hover:border-slate-600 transition-all group`}
            >
              <Icon size={24} className="text-white mb-2" />
              <h3 className="text-sm font-semibold text-white">
                {platform.name}
              </h3>
              <p className="text-xs text-slate-300 mt-1">
                {platform.description}
              </p>
            </motion.button>
          );
        })}
      </div>

      {/* Connected Accounts */}
      <div className="mt-8">
        <h3 className="text-sm font-semibold text-slate-300 mb-3">
          Connected Accounts
        </h3>
        <motion.button
          whileHover={{ scale: 1.02 }}
          className="w-full flex items-center gap-3 p-4 rounded-lg border-2 border-dashed border-slate-700 hover:border-slate-600 transition-colors"
        >
          <Plus size={20} className="text-slate-400" />
          <span className="text-sm font-medium text-slate-300">
            Connect New Account
          </span>
        </motion.button>
      </div>
    </div>
  );
}
