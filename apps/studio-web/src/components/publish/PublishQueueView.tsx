"use client";

import { motion } from "framer-motion";
import { Clock, AlertCircle, CheckCircle } from "lucide-react";

interface PublishQueueViewProps {
  jobs: any[];
}

export function PublishQueueView({ jobs }: PublishQueueViewProps) {
  if (!jobs.length) {
    return (
      <div className="text-center py-12 text-slate-400">
        <p>No jobs in queue</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {jobs.map((job) => (
        <motion.div
          key={job.id}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-4 rounded-lg border border-slate-700 bg-slate-800/30 hover:border-slate-600 transition-colors"
        >
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Clock size={16} className="text-blue-400" />
                <span className="font-semibold text-white">
                  Queued for {job.platform}
                </span>
              </div>
              {job.scheduled_time && (
                <p className="text-xs text-slate-400">
                  Scheduled for {new Date(job.scheduled_time).toLocaleString()}
                </p>
              )}
            </div>
            <button className="px-3 py-1.5 text-xs rounded bg-slate-700 hover:bg-slate-600 text-slate-300 transition-colors">
              Cancel
            </button>
          </div>
        </motion.div>
      ))}
    </div>
  );
}
