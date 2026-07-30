"use client";

import { motion } from "framer-motion";
import { Clock } from "lucide-react";

const posts = [
  {
    title: "Web Development Trends",
    platform: "YouTube",
    time: "Tomorrow 9 PM",
  },
  {
    title: "Data Science Deep Dive",
    platform: "YouTube Shorts",
    time: "Thursday 10 AM",
  },
  { title: "AI Ethics Discussion", platform: "LinkedIn", time: "Friday 2 PM" },
];

export function UpcomingPosts({ projectId }: { projectId: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-6 rounded-lg border border-slate-700 bg-slate-800/30"
    >
      <div className="flex items-center gap-2 mb-4">
        <Clock size={20} className="text-purple-400" />
        <h2 className="text-lg font-semibold text-white">Scheduled Posts</h2>
      </div>
      <div className="space-y-3">
        {posts.map((post, idx) => (
          <motion.div
            key={idx}
            className="flex items-center justify-between p-3 rounded-lg bg-slate-900/50"
          >
            <div>
              <p className="text-sm font-medium text-white">{post.title}</p>
              <p className="text-xs text-slate-500">{post.platform}</p>
            </div>
            <p className="text-xs text-purple-400 font-medium whitespace-nowrap ml-2">
              {post.time}
            </p>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
