"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import ReviewHeader from "./ReviewHeader";
import VideoPlayer from "./VideoPlayer";
import AIReviewPanel from "./AIReviewPanel";
import SceneTimeline from "./SceneTimeline";
import ChatSidebar from "./ChatSidebar";
import ActionBar from "./ActionBar";
import AnalysisProgress from "./AnalysisProgress";
import { fetchAnalysis } from "@/lib/api/analysis";

interface ReviewLayoutProps {
  projectId: string;
}

export default function ReviewLayout({ projectId }: ReviewLayoutProps) {
  const [selectedSuggestion, setSelectedSuggestion] = useState<string | null>(
    null
  );
  const [acceptedSuggestions, setAcceptedSuggestions] = useState<Set<string>>(
    new Set()
  );

  const {
    data: analysis,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["analysis", projectId],
    queryFn: () => fetchAnalysis(projectId),
  });

  if (isLoading) {
    return <AnalysisProgress />;
  }

  if (error || !analysis) {
    return (
      <div className="h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
        <div className="text-center">
          <p className="text-xl text-slate-400">Failed to load analysis</p>
          <p className="text-sm text-slate-500 mt-2">Please try again</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      <ReviewHeader projectId={projectId} analysis={analysis} />

      <div className="flex h-[calc(100vh-120px)]">
        {/* Left: Video Player */}
        <div className="flex-1 border-r border-slate-800 overflow-y-auto">
          <VideoPlayer analysis={analysis} />
          <SceneTimeline scenes={analysis.scenes} />
        </div>

        {/* Middle: AI Review */}
        <div className="flex-1 overflow-y-auto border-r border-slate-800">
          <AIReviewPanel
            analysis={analysis}
            selectedSuggestion={selectedSuggestion}
            acceptedSuggestions={acceptedSuggestions}
            onSuggestionSelect={setSelectedSuggestion}
            onSuggestionAccept={(id) => {
              setAcceptedSuggestions((prev) => new Set([...prev, id]));
            }}
          />
        </div>

        {/* Right: Chat Sidebar */}
        <div className="w-80 border-l border-slate-800 overflow-y-auto">
          <ChatSidebar projectId={projectId} />
        </div>
      </div>

      {/* Bottom Action Bar */}
      <ActionBar
        acceptedCount={acceptedSuggestions.size}
        totalSuggestions={analysis.suggestions.length}
      />
    </div>
  );
}
