"use client";

import { motion } from "framer-motion";
import { Check, Loader } from "lucide-react";

interface AnalysisProgressProps {
  status: string;
}

export default function AnalysisProgress({ status }: AnalysisProgressProps) {
  const steps = [
    { name: "Scene Detection", key: "scene_detection" },
    { name: "Speech Recognition", key: "speech" },
    { name: "Emotion Detection", key: "emotion" },
    { name: "Suggestion Generation", key: "suggestions" },
    { name: "Review Generation", key: "review" },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4"
    >
      <div className="space-y-3">
        {steps.map((step) => {
          const isCompleted = false;
          const isActive = step.key === status;

          return (
            <div key={step.key} className="flex items-center gap-3">
              {isCompleted ? (
                <div className="w-6 h-6 rounded-full bg-green-600 flex items-center justify-center flex-shrink-0">
                  <Check size={16} className="text-white" />
                </div>
              ) : isActive ? (
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                  className="w-6 h-6 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0"
                >
                  <Loader size={16} className="text-white" />
                </motion.div>
              ) : (
                <div className="w-6 h-6 rounded-full bg-slate-700 flex-shrink-0" />
              )}

              <span
                className={`text-sm ${
                  isCompleted || isActive ? "text-white" : "text-slate-500"
                }`}
              >
                {step.name}
              </span>
            </div>
          );
        })}
      </div>

      <div className="text-xs text-slate-500 text-center">
        <motion.div
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          Analyzing your video...
        </motion.div>
      </div>
    </motion.div>
  );
}
