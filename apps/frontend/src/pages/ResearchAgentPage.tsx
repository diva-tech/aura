"""
ResearchAgent Dashboard UI Page.

Real-time visualization of autonomous agent execution.
Shows goal, state, timeline, steps, tools, LLM, and metrics.
"""

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AlertCircle, CheckCircle, Clock, Zap, DollarSign, Target } from "lucide-react";

interface ExecutionMetrics {
  totalTime: number;
  planningTime: number;
  executionTime: number;
  reflectionTime: number;
  totalTokens: number;
  estimatedCost: number;
  toolCalls: number;
  reflections: number;
  replans: number;
}

interface Step {
  id: string;
  index: number;
  description: string;
  status: "pending" | "running" | "completed" | "failed" | "skipped";
  tool?: string;
  duration?: number;
  output?: string;
}

interface Goal {
  id: string;
  description: string;
  status: "accepted" | "planning" | "executing" | "reflecting" | "replanning" | "completed" | "failed";
}

export default function ResearchAgentPage() {
  const [goal, setGoal] = useState<Goal>({
    id: "goal-001",
    description: "Research Java 21 features and new capabilities",
    status: "executing",
  });

  const [state, setState] = useState<string>("EXECUTING");

  const [steps, setSteps] = useState<Step[]>([
    {
      id: "step-1",
      index: 1,
      description: "Search for Java 21 official documentation",
      status: "completed",
      tool: "BrowserTool",
      duration: 2340,
    },
    {
      id: "step-2",
      index: 2,
      description: "Extract key features and improvements",
      status: "completed",
      tool: "PythonTool",
      duration: 1850,
    },
    {
      id: "step-3",
      index: 3,
      description: "Search for Java 21 performance benchmarks",
      status: "running",
      tool: "BrowserTool",
      duration: 340,
    },
    {
      id: "step-4",
      index: 4,
      description: "Analyze performance improvements",
      status: "pending",
    },
    {
      id: "step-5",
      index: 5,
      description: "Compile final findings",
      status: "pending",
    },
  ]);

  const [metrics, setMetrics] = useState<ExecutionMetrics>({
    totalTime: 4530,
    planningTime: 1200,
    executionTime: 2300,
    reflectionTime: 1030,
    totalTokens: 2150,
    estimatedCost: 0.0315,
    toolCalls: 3,
    reflections: 2,
    replans: 0,
  });

  const getStatusColor = (status: string): string => {
    const colors: Record<string, string> = {
      completed: "bg-green-100 text-green-800",
      running: "bg-blue-100 text-blue-800",
      failed: "bg-red-100 text-red-800",
      pending: "bg-gray-100 text-gray-800",
      skipped: "bg-yellow-100 text-yellow-800",
      planning: "bg-blue-100 text-blue-800",
      executing: "bg-purple-100 text-purple-800",
      reflecting: "bg-orange-100 text-orange-800",
    };
    return colors[status] || "bg-gray-100 text-gray-800";
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case "failed":
        return <AlertCircle className="w-5 h-5 text-red-600" />;
      case "running":
        return <Zap className="w-5 h-5 text-blue-600" />;
      default:
        return <Clock className="w-5 h-5 text-gray-600" />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-slate-900 mb-2">ResearchAgent Dashboard</h1>
          <p className="text-slate-600">Real-time autonomous research agent execution</p>
        </div>

        {/* Goal Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="w-5 h-5" />
              Current Goal
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm text-slate-600 mb-2">Goal Description</p>
              <p className="text-lg font-semibold text-slate-900">{goal.description}</p>
            </div>
            <div className="flex items-center gap-4">
              <div>
                <p className="text-sm text-slate-600 mb-1">Goal ID</p>
                <p className="font-mono text-sm text-slate-700">{goal.id}</p>
              </div>
              <div>
                <p className="text-sm text-slate-600 mb-1">Status</p>
                <Badge className={getStatusColor(goal.status)}>{goal.status.toUpperCase()}</Badge>
              </div>
              <div>
                <p className="text-sm text-slate-600 mb-1">Agent State</p>
                <Badge className={getStatusColor(state.toLowerCase())}>{state}</Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Two-column layout */}
        <div className="grid grid-cols-3 gap-6">
          {/* Left column: Steps and Timeline */}
          <div className="col-span-2 space-y-6">
            {/* Execution Timeline */}
            <Card>
              <CardHeader>
                <CardTitle>Execution Timeline</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between items-center py-2 border-b">
                    <span className="text-slate-600">Planning Phase</span>
                    <span className="font-mono text-slate-900">{metrics.planningTime}ms</span>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b">
                    <span className="text-slate-600">Execution Phase</span>
                    <span className="font-mono text-slate-900">{metrics.executionTime}ms</span>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b">
                    <span className="text-slate-600">Reflection Phase</span>
                    <span className="font-mono text-slate-900">{metrics.reflectionTime}ms</span>
                  </div>
                  <div className="flex justify-between items-center py-2 font-semibold">
                    <span className="text-slate-900">Total Time</span>
                    <span className="font-mono text-slate-900">
                      {(metrics.totalTime / 1000).toFixed(1)}s
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Steps Execution */}
            <Card>
              <CardHeader>
                <CardTitle>Execution Steps</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {steps.map((step, idx) => (
                  <div key={step.id} className="border rounded-lg p-4 hover:bg-slate-50 transition">
                    <div className="flex items-start gap-3">
                      {getStatusIcon(step.status)}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-sm font-semibold text-slate-700">Step {step.index}</span>
                          <Badge className={getStatusColor(step.status)}>{step.status}</Badge>
                          {step.tool && (
                            <Badge variant="outline" className="text-xs">
                              {step.tool}
                            </Badge>
                          )}
                        </div>
                        <p className="text-slate-700">{step.description}</p>
                        {step.duration && (
                          <p className="text-xs text-slate-500 mt-2">
                            ⏱️ {(step.duration / 1000).toFixed(2)}s
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Right column: Metrics */}
          <div className="space-y-6">
            {/* LLM Metrics */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm flex items-center gap-2">
                  <Zap className="w-4 h-4" />
                  LLM Usage
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3 text-sm">
                <div>
                  <p className="text-slate-600 text-xs uppercase">Tokens</p>
                  <p className="text-2xl font-bold text-slate-900">{metrics.totalTokens}</p>
                </div>
                <div className="border-t pt-3">
                  <p className="text-slate-600 text-xs uppercase">Cost</p>
                  <p className="text-2xl font-bold text-slate-900">
                    ${metrics.estimatedCost.toFixed(4)}
                  </p>
                </div>
                <div className="border-t pt-3">
                  <p className="text-slate-600 text-xs uppercase">Reflections</p>
                  <p className="text-2xl font-bold text-slate-900">{metrics.reflections}</p>
                </div>
                <div className="border-t pt-3">
                  <p className="text-slate-600 text-xs uppercase">Replans</p>
                  <p className="text-2xl font-bold text-slate-900">{metrics.replans}</p>
                </div>
              </CardContent>
            </Card>

            {/* Tool Metrics */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Tool Calls</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-600">Total Calls</span>
                    <span className="text-xl font-bold text-slate-900">{metrics.toolCalls}</span>
                  </div>
                  <div className="border-t pt-3">
                    <p className="text-slate-600 text-xs uppercase mb-2">Tool Breakdown</p>
                    <div className="space-y-2">
                      <div className="flex justify-between text-xs">
                        <span>Browser</span>
                        <Badge variant="outline">2</Badge>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span>Python</span>
                        <Badge variant="outline">1</Badge>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Progress */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Progress</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="text-xs text-slate-600 mb-2">Steps Completed</p>
                  <div className="w-full bg-slate-200 rounded-full h-2">
                    <div
                      className="bg-green-600 h-2 rounded-full"
                      style={{ width: `${(2 / steps.length) * 100}%` }}
                    ></div>
                  </div>
                  <p className="text-xs text-slate-600 mt-1">
                    {steps.filter((s) => s.status === "completed").length} of {steps.length}
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Events Log */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Recent Events</CardTitle>
          </CardHeader>
          <CardContent className="max-h-48 overflow-y-auto">
            <div className="space-y-2 text-xs font-mono">
              <div className="text-slate-600">
                <span className="text-slate-900">[GoalAcceptedEvent]</span> Goal-001 accepted
              </div>
              <div className="text-slate-600">
                <span className="text-slate-900">[PlanningStartedEvent]</span> Planning started
              </div>
              <div className="text-slate-600">
                <span className="text-slate-900">[PlanningCompletedEvent]</span> 5 steps planned
              </div>
              <div className="text-slate-600">
                <span className="text-slate-900">[StepStartedEvent]</span> Step-1 started
              </div>
              <div className="text-slate-600">
                <span className="text-blue-600">[StepCompletedEvent]</span> Step-1 completed (2340ms)
              </div>
              <div className="text-slate-600">
                <span className="text-slate-900">[ReflectionStartedEvent]</span> Reflection-1 started
              </div>
              <div className="text-slate-600">
                <span className="text-blue-600">[ReflectionCompletedEvent]</span> Decision: CONTINUE
              </div>
              <div className="text-slate-600">
                <span className="text-slate-900">[StepStartedEvent]</span> Step-2 started
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
