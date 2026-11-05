"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Send, X } from "lucide-react";

interface PreviewCommentsProps {
  previewId: string;
}

export function PreviewComments({ previewId }: PreviewCommentsProps) {
  const [comments, setComments] = useState([
    {
      id: "1",
      timestamp: 45000,
      text: "Keep this scene - it's got great energy",
      author: "You",
      resolved: false,
    },
    {
      id: "2",
      timestamp: 120000,
      text: "Need to add more context here",
      author: "Reviewer",
      resolved: true,
    },
  ]);
  const [newComment, setNewComment] = useState("");

  const handleAddComment = () => {
    if (!newComment.trim()) return;

    const comment = {
      id: Date.now().toString(),
      timestamp: 0,
      text: newComment,
      author: "You",
      resolved: false,
    };
    setComments([...comments, comment]);
    setNewComment("");
  };

  return (
    <div className="flex flex-col h-full">
      <div className="px-4 py-3 border-b border-slate-800">
        <h3 className="text-sm font-semibold text-slate-300">Comments</h3>
        <p className="text-xs text-slate-500 mt-1">
          {comments.length} comments
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {comments.map((comment, idx) => (
          <motion.div
            key={comment.id}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.05 }}
            className={`p-3 rounded-lg border ${
              comment.resolved
                ? "border-slate-700 bg-slate-900/30 opacity-60"
                : "border-slate-700 bg-slate-800/30"
            }`}
          >
            <div className="flex items-start justify-between gap-2 mb-2">
              <div>
                <span className="text-xs font-medium text-slate-300">
                  {comment.author}
                </span>
                <span className="text-xs text-slate-500 ml-2">
                  @ {formatTime(comment.timestamp)}
                </span>
              </div>
              {comment.resolved && (
                <span className="text-xs px-2 py-0.5 rounded-full bg-green-900/30 text-green-300 font-medium">
                  Resolved
                </span>
              )}
            </div>
            <p className="text-sm text-slate-300 mb-2">{comment.text}</p>
            <div className="flex gap-2">
              <button className="text-xs px-2 py-1 rounded bg-slate-700/50 hover:bg-slate-700 text-slate-300 transition-colors">
                Reply
              </button>
              {!comment.resolved && (
                <button className="text-xs px-2 py-1 rounded bg-slate-700/50 hover:bg-slate-700 text-slate-300 transition-colors">
                  Resolve
                </button>
              )}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Comment input */}
      <div className="border-t border-slate-800 p-4 space-y-2">
        <textarea
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder="Add a comment..."
          className="w-full px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 text-sm resize-none h-20"
        />
        <button
          onClick={handleAddComment}
          className="w-full px-3 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium transition-colors flex items-center justify-center gap-2"
        >
          <Send size={14} />
          Post Comment
        </button>
      </div>
    </div>
  );
}

function formatTime(ms: number): string {
  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  return `${minutes}:${(seconds % 60).toString().padStart(2, "0")}`;
}
