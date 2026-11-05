"use client";

import { motion } from "framer-motion";
import { CheckCircle, AlertCircle } from "lucide-react";
import { ExternalLink } from "lucide-react";

interface PublishHistoryViewProps {
  publishedJobs: any[];
  failedJobs: any[];
}

export function PublishHistoryView({
  publishedJobs,
  failedJobs,
}: PublishHistoryViewProps) {
  return (
    <div className="space-y-6">
      {/* Published */}
      {publishedJobs.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-green-400 mb-3">
            Published ({publishedJobs.length})
          </h3>
          <div className="space-y-2">
            {publishedJobs.map((job) => (
              <motion.div
                key={job.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="p-3 rounded-lg border border-green-700/50 bg-green-900/20"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <CheckCircle size={16} className="text-green-400" />
                    <span className="text-sm text-white">
                      {job.platform} •{" "}
                      {new Date(job.published_at).toLocaleDateString()}
                    </span>
                  </div>
                  <a
                    href={job.platform_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-green-400 hover:text-green-300"
                  >
                    <ExternalLink size={16} />
                  </a>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Failed */}
      {failedJobs.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-red-400 mb-3">
            Failed ({failedJobs.length})
          </h3>
          <div className="space-y-2">
            {failedJobs.map((job) => (
              <motion.div
                key={job.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="p-3 rounded-lg border border-red-700/50 bg-red-900/20"
              >
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-2">
                    <AlertCircle size={16} className="text-red-400" />
                    <span className="text-sm text-white">{job.platform}</span>
                  </div>
                  <button className="text-xs px-2 py-1 rounded bg-red-900/50 hover:bg-red-900 text-red-300 transition-colors">
                    Retry
                  </button>
                </div>
                <p className="text-xs text-red-300">{job.error_message}</p>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {!publishedJobs.length && !failedJobs.length && (
        <div className="text-center py-8 text-slate-400">
          <p>No publish history</p>
        </div>
      )}
    </div>
  );
}
