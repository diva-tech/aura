/**
 * Keyboard Shortcuts Library
 * Consistent keyboard interaction patterns for premium UX
 */

import { useEffect } from "react";

interface KeyboardShortcut {
  key: string;
  ctrlKey?: boolean;
  shiftKey?: boolean;
  metaKey?: boolean;
  altKey?: boolean;
  handler: () => void;
}

/**
 * Register keyboard shortcut
 * @param shortcut - The keyboard shortcut configuration
 */
export function useKeyboardShortcut(shortcut: KeyboardShortcut) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const matches =
        e.key.toLowerCase() === shortcut.key.toLowerCase() &&
        (shortcut.ctrlKey === undefined || e.ctrlKey === shortcut.ctrlKey) &&
        (shortcut.shiftKey === undefined || e.shiftKey === shortcut.shiftKey) &&
        (shortcut.metaKey === undefined || e.metaKey === shortcut.metaKey) &&
        (shortcut.altKey === undefined || e.altKey === shortcut.altKey);

      if (matches) {
        e.preventDefault();
        shortcut.handler();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [shortcut]);
}

/**
 * Register multiple keyboard shortcuts
 */
export function useKeyboardShortcuts(shortcuts: KeyboardShortcut[]) {
  shortcuts.forEach((shortcut) => {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    useKeyboardShortcut(shortcut);
  });
}

/**
 * Common keyboard shortcuts
 */
export const SHORTCUTS = {
  // Navigation
  search: { key: "k", ctrlKey: true, metaKey: true }, // Cmd/Ctrl+K
  back: { key: "Escape" },
  forward: { key: "ArrowRight", ctrlKey: true, shiftKey: true },
  backward: { key: "ArrowLeft", ctrlKey: true, shiftKey: true },

  // Editing
  save: { key: "s", ctrlKey: true, metaKey: true }, // Cmd/Ctrl+S
  undo: { key: "z", ctrlKey: true, metaKey: true }, // Cmd/Ctrl+Z
  redo: { key: "z", ctrlKey: true, metaKey: true, shiftKey: true }, // Cmd/Ctrl+Shift+Z

  // Timeline
  play: { key: " " }, // Space
  playPause: { key: "k" }, // K (common in video players)
  frameForward: { key: "." },
  frameBackward: { key: "," },
  markIn: { key: "i" },
  markOut: { key: "o" },

  // UI
  fullscreen: { key: "f" },
  focus: { key: "Tab" },
};

/**
 * Format keyboard shortcut for display
 */
export function formatShortcut(shortcut: KeyboardShortcut): string {
  const parts: string[] = [];

  if (shortcut.metaKey) parts.push("Cmd");
  if (shortcut.ctrlKey) parts.push("Ctrl");
  if (shortcut.shiftKey) parts.push("Shift");
  if (shortcut.altKey) parts.push("Alt");

  // Format key name
  const keyDisplay =
    shortcut.key === " " ? "Space" : shortcut.key.toUpperCase();
  parts.push(keyDisplay);

  return parts.join(" + ");
}

/**
 * Check if a keyboard event matches a shortcut
 */
export function matchesShortcut(
  e: KeyboardEvent,
  shortcut: KeyboardShortcut
): boolean {
  return (
    e.key.toLowerCase() === shortcut.key.toLowerCase() &&
    (shortcut.ctrlKey === undefined || e.ctrlKey === shortcut.ctrlKey) &&
    (shortcut.shiftKey === undefined || e.shiftKey === shortcut.shiftKey) &&
    (shortcut.metaKey === undefined || e.metaKey === shortcut.metaKey) &&
    (shortcut.altKey === undefined || e.altKey === shortcut.altKey)
  );
}
