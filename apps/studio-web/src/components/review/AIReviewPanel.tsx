"use client";

import { motion } from "framer-motion";
import AIReviewCard from "./cards/AIReviewCard";
import CategoryCards from "./cards/CategoryCards";
import StrengthCard from "./cards/StrengthCard";
import ProblemCard from "./cards/ProblemCard";
import SuggestionCard from "./cards/SuggestionCard";

interface AIReviewPanelProps {
  analysis: any;
  selectedSuggestion: string | null;
  acceptedSuggestions: Set<string>;
  onSuggestionSelect: (id: string | null) => void;
  onSuggestionAccept: (id: string) => void;
}

export default function AIReviewPanel({
  analysis,
  selectedSuggestion,
  acceptedSuggestions,
  onSuggestionSelect,
  onSuggestionAccept,
}: AIReviewPanelProps) {
  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  return (
    <motion.div
      variants={container}
      initial="hidden"
      animate="show"
      className="space-y-6 p-8"
    >
      {/* AI Review Summary */}
      <AIReviewCard analysis={analysis} />

      {/* Category Scores */}
      <CategoryCards scores={analysis?.report} />

      {/* Strengths Section */}
      <div>
        <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
          <span>✓</span> Strengths
        </h3>
        <div className="space-y-2">
          {[
            "Excellent audio quality",
            "Clear explanation",
            "Strong market analysis",
          ].map((strength, idx) => (
            <StrengthCard key={idx} strength={strength} />
          ))}
        </div>
      </div>

      {/* Problems Section */}
      <div>
        <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
          <span>⚠</span> Areas for Improvement
        </h3>
        <div className="space-y-2">
          {["Intro too long", "Hook starts late", "Missing captions"].map(
            (problem, idx) => (
              <ProblemCard key={idx} problem={problem} />
            )
          )}
        </div>
      </div>

      {/* Suggestions Section */}
      <div>
        <h3 className="text-lg font-semibold text-white mb-3">
          AI Suggestions
        </h3>
        <div className="space-y-3">
          {analysis?.suggestions?.map((suggestion: any) => (
            <SuggestionCard
              key={suggestion.id}
              suggestion={suggestion}
              isSelected={selectedSuggestion === suggestion.id}
              isAccepted={acceptedSuggestions.has(suggestion.id)}
              onSelect={() => onSuggestionSelect(suggestion.id)}
              onAccept={() => onSuggestionAccept(suggestion.id)}
            />
          ))}
        </div>
      </div>

      <div className="h-20" />
    </motion.div>
  );
}
