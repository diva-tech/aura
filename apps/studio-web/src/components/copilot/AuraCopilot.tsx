"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Send,
  Sparkles,
  Lightbulb,
  ChevronDown,
  Plus,
  Zap,
} from "lucide-react";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface CopilotProps {
  projectId: string;
  isOpen: boolean;
  onToggle: () => void;
}

export function AuraCopilot({ projectId, isOpen, onToggle }: CopilotProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content:
        "Hi! I'm AURA, your creative AI assistant. I can help you " +
        "analyze videos, improve editing, optimize content, and " +
        "strategize your channel. What would you like to work on?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    // Simulate AI response
    setTimeout(() => {
      const responses = [
        "Based on your analytics, I see that video retention dropped after 32 seconds. Let's regenerate your edit plan with more engaging cuts in that section. I can help you restructure the pacing.",
        "Your best-performing videos trend toward 8-12 minute lengths with strong hooks in the first 3 seconds. I recommend your next video follow this pattern and upload at 9 PM when your audience is most active.",
        "I analyzed your YouTube Shorts performance and notice higher engagement with bright, text-heavy thumbnails. Want me to create a thumbnail concept prompt or regenerate metadata for your upcoming videos?",
      ];

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: responses[Math.floor(Math.random() * responses.length)],
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setIsLoading(false);
    }, 1000);
  };

  const quickActions = [
    { icon: Zap, label: "Analyze Video", action: "reanalyze" },
    { icon: Lightbulb, label: "Edit Plan", action: "generate_edit_plan" },
    { icon: Plus, label: "Thumbnail", action: "create_thumbnail" },
  ];

  return (
    <>
      {/* Floating button */}
      {!isOpen && (
        <motion.button
          layoutId="copilot-button"
          onClick={onToggle}
          className="fixed bottom-8 right-8 w-16 h-16 rounded-full bg-gradient-to-br from-purple-600 to-blue-600 shadow-lg flex items-center justify-center text-white hover:shadow-xl transition-shadow z-40"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
        >
          <Sparkles size={24} />
        </motion.button>
      )}

      {/* Copilot panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            layoutId="copilot-button"
            initial={{ opacity: 0, y: 20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.9 }}
            className="fixed bottom-8 right-8 w-96 h-[600px] rounded-2xl bg-gradient-to-b from-slate-900 to-slate-950 border border-slate-700 shadow-2xl flex flex-col overflow-hidden z-50"
          >
            {/* Header */}
            <div className="bg-gradient-to-r from-purple-600 to-blue-600 p-4 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles size={20} className="text-white" />
                <h2 className="text-lg font-semibold text-white">AURA</h2>
              </div>
              <button
                onClick={onToggle}
                className="p-1 hover:bg-white/20 rounded transition-colors"
              >
                <ChevronDown size={20} className="text-white" />
              </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
              {messages.map((msg) => (
                <motion.div
                  key={msg.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex ${
                    msg.role === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  <div
                    className={`max-w-xs rounded-lg p-3 text-sm ${
                      msg.role === "user"
                        ? "bg-blue-600 text-white"
                        : "bg-slate-800 text-slate-200"
                    }`}
                  >
                    {msg.content}
                  </div>
                </motion.div>
              ))}
              {isLoading && (
                <motion.div
                  animate={{ opacity: [0.5, 1, 0.5] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                  className="flex gap-1 p-3"
                >
                  <div className="w-2 h-2 bg-slate-600 rounded-full" />
                  <div className="w-2 h-2 bg-slate-600 rounded-full" />
                  <div className="w-2 h-2 bg-slate-600 rounded-full" />
                </motion.div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Quick actions */}
            <div className="px-4 py-2 border-t border-slate-700 flex gap-2">
              {quickActions.map((action) => {
                const Icon = action.icon;
                return (
                  <motion.button
                    key={action.action}
                    whileHover={{ scale: 1.05 }}
                    className="flex-1 px-2 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-300 transition-colors flex items-center justify-center gap-1"
                  >
                    <Icon size={14} />
                    {action.label}
                  </motion.button>
                );
              })}
            </div>

            {/* Input */}
            <div className="p-4 border-t border-slate-700 flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleSend()}
                placeholder="Ask AURA..."
                className="flex-1 px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 text-sm"
              />
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleSend}
                disabled={isLoading}
                className="px-3 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white transition-colors disabled:opacity-50"
              >
                <Send size={18} />
              </motion.button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
