"use client";

import { motion } from "framer-motion";
import { Play } from "lucide-react";

interface VideoPlayerProps {
  analysis: any;
}

export default function VideoPlayer({ analysis }: VideoPlayerProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="p-6 space-y-4"
    >
      <div className="aspect-video rounded-xl bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 flex items-center justify-center group hover:border-slate-600 transition-colors cursor-pointer">
        <div className="absolute flex items-center justify-center">
          <div className="w-20 h-20 rounded-full bg-white/20 backdrop-blur-md flex items-center justify-center group-hover:bg-white/30 transition-colors">
            <Play size={32} className="text-white fill-white ml-1" />
          </div>
        </div>
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="text-slate-400">0:00</span>
          <span className="text-slate-400">
            {analysis?.report?.duration || 0}s
          </span>
        </div>
        <div className="w-full bg-slate-700 rounded-full h-1">
          <div
            className="bg-blue-500 h-1 rounded-full"
            style={{ width: "0%" }}
          />
        </div>
      </div>

      <div className="grid grid-cols-3 gap-2 text-xs text-slate-400">
        <div className="bg-slate-800/50 rounded p-2">
          <div className="font-medium text-slate-300">FPS</div>
          <div>{analysis?.metrics?.fps || 30}</div>
        </div>
        <div className="bg-slate-800/50 rounded p-2">
          <div className="font-medium text-slate-300">Resolution</div>
          <div>{analysis?.metrics?.resolution || "1080p"}</div>
        </div>
        <div className="bg-slate-800/50 rounded p-2">
          <div className="font-medium text-slate-300">Bitrate</div>
          <div>{analysis?.metrics?.bitrate || "5Mbps"}</div>
        </div>
      </div>
    </motion.div>
  );
}
