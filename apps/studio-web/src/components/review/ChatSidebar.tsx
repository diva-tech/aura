"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Send } from "lucide-react";

interface ChatSidebarProps {
  projectId: string;
}

export default function ChatSidebar({ projectId }: ChatSidebarProps) {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState("");

  const suggestions = [
    "How can this become viral?",
    "Should I publish this?",
    "Can you improve the hook?",
    "Why remove the intro?",
  ];

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="h-full flex flex-col p-6 space-y-4"
    >
      <div>
        <h3 className="text-lg font-semibold text-white mb-1">Ask AURA</h3>
        <p className="text-xs text-slate-500">
          Get personalized recommendations
        </p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-3">
        {messages.length === 0 && (
          <div className="space-y-2">
            <p className="text-xs text-slate-500 mb-3">Suggested questions:</p>
            {suggestions.map((suggestion, idx) => (
              <motion.button
                key={idx}
                whileHover={{ scale: 1.02, x: 5 }}
                onClick={() => setInput(suggestion)}
                className="w-full text-left text-sm p-3 rounded-lg bg-slate-800/50 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-700 transition-colors"
              >
                {suggestion}
              </motion.button>
            ))}
          </div>
        )}
      </div>

      {/* Input */}
      <div className="border-t border-slate-800 pt-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask a question..."
            className="flex-1 px-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-slate-600 text-sm"
          />
          <button className="p-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white transition-colors">
            <Send size={18} />
          </button>
        </div>
      </div>
    </motion.div>
  );
}
