"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Send, X } from "lucide-react";

interface PublishMetadataFormProps {
  platform: string;
  projectId: string;
  onClose: () => void;
}

export function PublishMetadataForm({
  platform,
  projectId,
  onClose,
}: PublishMetadataFormProps) {
  const [metadata, setMetadata] = useState({
    title: "",
    description: "",
    tags: "",
    caption: "",
    hashtags: "",
    scheduledTime: "",
  });

  const handlePublish = async () => {
    // Publish logic would go here
    console.log("Publishing to", platform, metadata);
    onClose();
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 20 }}
      className="rounded-lg border border-blue-700/50 bg-blue-900/20 p-6"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">
          Publish to {platform.toUpperCase()}
        </h3>
        <button
          onClick={onClose}
          className="p-1 rounded hover:bg-blue-800/30 text-slate-400 hover:text-white transition-colors"
        >
          <X size={20} />
        </button>
      </div>

      <div className="space-y-4">
        {/* Title */}
        {(platform === "youtube" || platform === "shorts") && (
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-2">
              Title
            </label>
            <input
              type="text"
              value={metadata.title}
              onChange={(e) =>
                setMetadata({ ...metadata, title: e.target.value })
              }
              placeholder="Video title"
              className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 text-sm"
            />
          </div>
        )}

        {/* Description */}
        {(platform === "youtube" || platform === "shorts") && (
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-2">
              Description
            </label>
            <textarea
              value={metadata.description}
              onChange={(e) =>
                setMetadata({ ...metadata, description: e.target.value })
              }
              placeholder="Video description"
              className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 text-sm resize-none h-24"
            />
          </div>
        )}

        {/* Caption */}
        {(platform === "instagram" || platform === "tiktok") && (
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-2">
              Caption
            </label>
            <textarea
              value={metadata.caption}
              onChange={(e) =>
                setMetadata({ ...metadata, caption: e.target.value })
              }
              placeholder="Post caption"
              className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 text-sm resize-none h-24"
            />
          </div>
        )}

        {/* Hashtags */}
        {(platform === "instagram" || platform === "tiktok") && (
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-2">
              Hashtags
            </label>
            <input
              type="text"
              value={metadata.hashtags}
              onChange={(e) =>
                setMetadata({ ...metadata, hashtags: e.target.value })
              }
              placeholder="#trending #viral"
              className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 text-sm"
            />
          </div>
        )}

        {/* Schedule */}
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-2">
            Schedule (Optional)
          </label>
          <input
            type="datetime-local"
            value={metadata.scheduledTime}
            onChange={(e) =>
              setMetadata({ ...metadata, scheduledTime: e.target.value })
            }
            className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-white focus:outline-none focus:border-blue-500 text-sm"
          />
        </div>

        {/* Buttons */}
        <div className="flex gap-2 pt-4">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-white text-sm font-medium transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handlePublish}
            className="flex-1 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium transition-colors flex items-center justify-center gap-2"
          >
            <Send size={16} />
            Publish
          </button>
        </div>
      </div>
    </motion.div>
  );
}
