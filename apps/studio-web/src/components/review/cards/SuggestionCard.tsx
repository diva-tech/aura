"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown } from "lucide-react";

interface SuggestionCardProps {
  suggestion: any;
  isSelected: boolean;
  isAccepted: boolean;
  onSelect: () => void;
  onAccept: () => void;
}

export default function SuggestionCard({
  suggestion,
  isSelected,
  isAccepted,
  onSelect,
  onAccept,
}: SuggestionCardProps) {
  const difficultyColor = {
    Easy: "text-green-400 bg-green-400/10",
    Medium: "text-yellow-400 bg-yellow-400/10",
    Hard: "text-red-400 bg-red-400/10",
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`rounded-xl border transition-all overflow-hidden ${
        isSelected
          ? "border-blue-500 bg-blue-500/5"
          : "border-slate-700 bg-slate-800/30 hover:border-slate-600"
      }`}
    >
      <button
        onClick={onSelect}
        className="w-full px-4 py-4 text-left flex items-start justify-between"
      >
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h4 className="font-semibold text-white">{suggestion.title}</h4>
            <span
              className={`text-xs px-2 py-1 rounded-md ${
                difficultyColor[
                  suggestion.difficulty as keyof typeof difficultyColor
                ] || ""
              }`}
            >
              {suggestion.difficulty}
            </span>
          </div>
          <div className="flex items-center gap-4 text-sm text-slate-400">
            <span>Confidence: {suggestion.confidence}%</span>
            <span>•</span>
            <span className="text-green-400">
              +{suggestion.estimated_impact}% Retention
            </span>
          </div>
        </div>

        <ChevronDown
          size={20}
          className={`text-slate-400 transition-transform ${isSelected ? "rotate-180" : ""}`}
        />
      </button>

      <AnimatePresence>
        {isSelected && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="border-t border-slate-700 px-4 py-4 bg-slate-900/50"
          >
            <p className="text-sm text-slate-300 mb-4">
              {suggestion.description}
            </p>

            <div className="bg-slate-800/50 rounded-lg p-3 mb-4">
              <p className="text-xs text-slate-400 mb-2 font-medium">Why?</p>
              <p className="text-sm text-slate-300">{suggestion.reason}</p>
            </div>

            <div className="flex gap-3">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={onAccept}
                disabled={isAccepted}
                className="flex-1 px-3 py-2 rounded-lg bg-green-600 hover:bg-green-700 text-white text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isAccepted ? "✓ Accepted" : "Accept"}
              </motion.button>
              <button className="flex-1 px-3 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 text-white text-sm font-medium transition-colors">
                Reject
              </button>
              <button className="flex-1 px-3 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 text-white text-sm font-medium transition-colors">
                Later
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
