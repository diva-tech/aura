"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Search,
  Command,
  ChevronRight,
  Zap,
  Settings,
  HelpCircle,
} from "lucide-react";

interface Command {
  id: string;
  label: string;
  description?: string;
  category: string;
  icon?: React.ReactNode;
  shortcut?: string;
  action: () => void;
}

interface CommandPaletteProps {
  commands: Command[];
}

export function CommandPalette({ commands }: CommandPaletteProps) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);

  // Filter and group commands
  const filtered = commands.filter(
    (cmd) =>
      cmd.label.toLowerCase().includes(search.toLowerCase()) ||
      cmd.category.toLowerCase().includes(search.toLowerCase())
  );

  const grouped = filtered.reduce(
    (acc, cmd) => {
      if (!acc[cmd.category]) {
        acc[cmd.category] = [];
      }
      acc[cmd.category].push(cmd);
      return acc;
    },
    {} as Record<string, Command[]>
  );

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Cmd/Ctrl + K to open
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setOpen(!open);
        setSearch("");
      }

      // Escape to close
      if (e.key === "Escape" && open) {
        setOpen(false);
      }

      // Arrow keys to navigate
      if (open) {
        if (e.key === "ArrowDown") {
          e.preventDefault();
          setSelectedIndex((i) => (i + 1) % filtered.length);
        }
        if (e.key === "ArrowUp") {
          e.preventDefault();
          setSelectedIndex((i) => (i - 1 + filtered.length) % filtered.length);
        }
        if (e.key === "Enter") {
          e.preventDefault();
          if (filtered[selectedIndex]) {
            filtered[selectedIndex].action();
            setOpen(false);
          }
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [open, filtered, selectedIndex]);

  return (
    <>
      {/* Trigger Button */}
      <motion.button
        onClick={() => setOpen(true)}
        className="hidden md:flex items-center gap-2 px-4 py-2 rounded-lg border border-slate-700 bg-slate-800/50 text-slate-400 hover:bg-slate-800 transition-colors text-sm"
      >
        <Search size={16} />
        <span>Search...</span>
        <span className="ml-auto text-xs text-slate-500 flex items-center gap-1">
          <Command size={12} />
          <span>K</span>
        </span>
      </motion.button>

      {/* Backdrop */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setOpen(false)}
            className="fixed inset-0 z-50 bg-black/50"
          />
        )}
      </AnimatePresence>

      {/* Palette */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="fixed left-1/2 top-24 z-50 w-full max-w-2xl -translate-x-1/2 rounded-lg border border-slate-700 bg-slate-900 shadow-2xl overflow-hidden"
          >
            {/* Search Input */}
            <div className="border-b border-slate-700 p-4 flex items-center gap-3">
              <Search size={20} className="text-slate-500" />
              <input
                autoFocus
                type="text"
                placeholder="Search commands, pages, actions..."
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setSelectedIndex(0);
                }}
                className="flex-1 bg-transparent text-white placeholder-slate-500 outline-none text-lg"
              />
            </div>

            {/* Commands List */}
            <div className="max-h-96 overflow-y-auto">
              {filtered.length === 0 ? (
                <div className="p-8 text-center">
                  <Search size={32} className="mx-auto mb-3 text-slate-600" />
                  <p className="text-slate-400">No commands found</p>
                </div>
              ) : (
                Object.entries(grouped).map(([category, cmds]) => (
                  <div
                    key={category}
                    className="border-t border-slate-800 first:border-t-0"
                  >
                    <div className="px-4 py-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                      {category}
                    </div>
                    <div className="space-y-1 px-2 py-2">
                      {cmds.map((cmd, idx) => {
                        const globalIdx = filtered.findIndex(
                          (c) => c.id === cmd.id
                        );
                        const isSelected = globalIdx === selectedIndex;

                        return (
                          <motion.button
                            key={cmd.id}
                            onClick={() => {
                              cmd.action();
                              setOpen(false);
                            }}
                            className={`w-full px-3 py-2 rounded-lg text-left text-sm transition-colors flex items-center justify-between ${
                              isSelected
                                ? "bg-blue-600 text-white"
                                : "text-slate-300 hover:bg-slate-800"
                            }`}
                          >
                            <div className="flex items-center gap-3">
                              {cmd.icon && (
                                <span className="text-base">{cmd.icon}</span>
                              )}
                              <div>
                                <p className="font-medium">{cmd.label}</p>
                                {cmd.description && (
                                  <p
                                    className={`text-xs ${
                                      isSelected
                                        ? "text-blue-100"
                                        : "text-slate-500"
                                    }`}
                                  >
                                    {cmd.description}
                                  </p>
                                )}
                              </div>
                            </div>
                            {cmd.shortcut && (
                              <span
                                className={`text-xs font-mono ${
                                  isSelected
                                    ? "text-blue-100"
                                    : "text-slate-500"
                                }`}
                              >
                                {cmd.shortcut}
                              </span>
                            )}
                          </motion.button>
                        );
                      })}
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Footer Hint */}
            <div className="border-t border-slate-800 px-4 py-3 flex items-center justify-between text-xs text-slate-500">
              <div className="flex items-center gap-4">
                <span>
                  <kbd className="px-2 py-1 rounded bg-slate-800">↑</kbd>
                  <kbd className="px-2 py-1 rounded bg-slate-800">↓</kbd>{" "}
                  Navigate
                </span>
                <span>
                  <kbd className="px-2 py-1 rounded bg-slate-800">Enter</kbd>{" "}
                  Select
                </span>
              </div>
              <span>
                <kbd className="px-2 py-1 rounded bg-slate-800">Esc</kbd> Close
              </span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
