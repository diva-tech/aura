"use client";

import { motion } from "framer-motion";
import { Download, FileVideo, FileText, Image, FileJson } from "lucide-react";

interface DownloadCenterProps {
  renders: any[];
}

export function DownloadCenter({ renders }: DownloadCenterProps) {
  if (!renders.length) {
    return (
      <div className="text-center py-12 text-slate-400">
        <p>No completed renders yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {renders.map((render) => (
        <motion.div
          key={render.id}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="rounded-lg border border-slate-700 bg-slate-800/30 overflow-hidden"
        >
          {/* Header */}
          <div className="p-4 border-b border-slate-700/50">
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold text-white">
                Render v{render.version || 1}
              </h3>
              <span className="text-xs text-slate-400">
                {new Date(render.completed_at).toLocaleDateString()}
              </span>
            </div>
            <p className="text-sm text-slate-400">
              {render.quality} • {render.resolution} • {render.codec}
            </p>
          </div>

          {/* Assets */}
          <div className="p-4 space-y-2">
            {/* Video */}
            <motion.a
              href={render.output_path}
              download
              whileHover={{ x: 4 }}
              className="flex items-center gap-3 p-3 rounded-lg bg-slate-800/50 hover:bg-slate-700/50 transition-colors group"
            >
              <FileVideo size={20} className="text-blue-400 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">
                  video.mp4
                </p>
                <p className="text-xs text-slate-500">
                  {Math.round((render.output_size || 0) / 1024 / 1024)}MB
                </p>
              </div>
              <Download
                size={16}
                className="text-slate-500 group-hover:text-white transition-colors flex-shrink-0"
              />
            </motion.a>

            {/* Captions */}
            <motion.button
              whileHover={{ x: 4 }}
              className="w-full flex items-center gap-3 p-3 rounded-lg bg-slate-800/50 hover:bg-slate-700/50 transition-colors group text-left"
            >
              <FileText size={20} className="text-green-400 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">
                  captions.srt
                </p>
                <p className="text-xs text-slate-500">Subtitles</p>
              </div>
              <Download
                size={16}
                className="text-slate-500 group-hover:text-white transition-colors flex-shrink-0"
              />
            </motion.button>

            {/* Thumbnail */}
            <motion.button
              whileHover={{ x: 4 }}
              className="w-full flex items-center gap-3 p-3 rounded-lg bg-slate-800/50 hover:bg-slate-700/50 transition-colors group text-left"
            >
              <Image size={20} className="text-yellow-400 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">
                  thumbnail.jpg
                </p>
                <p className="text-xs text-slate-500">Cover image</p>
              </div>
              <Download
                size={16}
                className="text-slate-500 group-hover:text-white transition-colors flex-shrink-0"
              />
            </motion.button>

            {/* Metadata */}
            <motion.button
              whileHover={{ x: 4 }}
              className="w-full flex items-center gap-3 p-3 rounded-lg bg-slate-800/50 hover:bg-slate-700/50 transition-colors group text-left"
            >
              <FileJson size={20} className="text-purple-400 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">
                  metadata.json
                </p>
                <p className="text-xs text-slate-500">Render report</p>
              </div>
              <Download
                size={16}
                className="text-slate-500 group-hover:text-white transition-colors flex-shrink-0"
              />
            </motion.button>
          </div>
        </motion.div>
      ))}
    </div>
  );
}
