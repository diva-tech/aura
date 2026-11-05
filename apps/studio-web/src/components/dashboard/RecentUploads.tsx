"use client";

import { motion } from "framer-motion";
import { Upload } from "lucide-react";

const uploads = [
  { title: "AI in 2026", views: "12,450", date: "2 days ago" },
  { title: "Machine Learning Basics", views: "8,320", date: "5 days ago" },
  { title: "Cloud Computing 101", views: "6,890", date: "1 week ago" },
];

export function RecentUploads({ projectId }: { projectId: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-6 rounded-lg border border-slate-700 bg-slate-800/30"
    >
      <div className="flex items-center gap-2 mb-4">
        <Upload size={20} className="text-blue-400" />
        <h2 className="text-lg font-semibold text-white">Recent Uploads</h2>
      </div>
      <div className="space-y-3">
        {uploads.map((upload, idx) => (
          <motion.div
            key={idx}
            className="flex items-center justify-between p-3 rounded-lg bg-slate-900/50"
          >
            <div>
              <p className="text-sm font-medium text-white">{upload.title}</p>
              <p className="text-xs text-slate-500">{upload.date}</p>
            </div>
            <p className="text-sm font-semibold text-blue-400">
              {upload.views}
            </p>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
