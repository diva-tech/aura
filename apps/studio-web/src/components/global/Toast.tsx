"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle, AlertCircle, Info, XCircle, X } from "lucide-react";

export type ToastType = "success" | "error" | "warning" | "info";

export interface Toast {
  id: string;
  message: string;
  type: ToastType;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

const typeConfig = {
  success: {
    icon: CheckCircle,
    bgColor: "bg-green-500/10",
    borderColor: "border-green-500/50",
    textColor: "text-green-300",
    iconColor: "text-green-400",
  },
  error: {
    icon: XCircle,
    bgColor: "bg-red-500/10",
    borderColor: "border-red-500/50",
    textColor: "text-red-300",
    iconColor: "text-red-400",
  },
  warning: {
    icon: AlertCircle,
    bgColor: "bg-amber-500/10",
    borderColor: "border-amber-500/50",
    textColor: "text-amber-300",
    iconColor: "text-amber-400",
  },
  info: {
    icon: Info,
    bgColor: "bg-blue-500/10",
    borderColor: "border-blue-500/50",
    textColor: "text-blue-300",
    iconColor: "text-blue-400",
  },
};

interface ToastContainerProps {
  toasts: Toast[];
  onRemove: (id: string) => void;
}

export function ToastContainer({ toasts, onRemove }: ToastContainerProps) {
  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-3 max-w-md">
      <AnimatePresence>
        {toasts.map((toast) => {
          const config = typeConfig[toast.type];
          const Icon = config.icon;

          return (
            <motion.div
              key={toast.id}
              initial={{ opacity: 0, y: 20, x: 400 }}
              animate={{ opacity: 1, y: 0, x: 0 }}
              exit={{ opacity: 0, y: 20, x: 400 }}
              className={`flex items-start gap-3 p-4 rounded-lg border ${config.bgColor} ${config.borderColor}`}
            >
              <Icon size={20} className={config.iconColor} />
              <div className="flex-1">
                <p className={`text-sm font-medium ${config.textColor}`}>
                  {toast.message}
                </p>
                {toast.action && (
                  <button
                    onClick={toast.action.onClick}
                    className={`text-xs font-medium mt-1 hover:underline ${config.textColor}`}
                  >
                    {toast.action.label}
                  </button>
                )}
              </div>
              <button
                onClick={() => onRemove(toast.id)}
                className="text-slate-500 hover:text-slate-300 transition-colors"
              >
                <X size={16} />
              </button>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}

// Toast hook for easy usage
export function useToast() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const show = (
    message: string,
    type: ToastType = "info",
    duration: number = 3000,
    action?: Toast["action"]
  ) => {
    const id = Date.now().toString();
    const toast: Toast = { id, message, type, duration, action };

    setToasts((prev) => [...prev, toast]);

    if (duration) {
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
      }, duration);
    }

    return id;
  };

  const remove = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  return {
    toasts,
    show,
    remove,
    success: (msg: string, duration?: number, action?: Toast["action"]) =>
      show(msg, "success", duration, action),
    error: (msg: string, duration?: number, action?: Toast["action"]) =>
      show(msg, "error", duration, action),
    warning: (msg: string, duration?: number, action?: Toast["action"]) =>
      show(msg, "warning", duration, action),
    info: (msg: string, duration?: number, action?: Toast["action"]) =>
      show(msg, "info", duration, action),
  };
}
