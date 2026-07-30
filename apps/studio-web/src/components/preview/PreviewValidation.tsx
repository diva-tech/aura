"use client";

import { motion } from "framer-motion";
import { CheckCircle, AlertCircle, AlertTriangle } from "lucide-react";

interface PreviewValidationProps {
  previewId: string;
}

export function PreviewValidation({ previewId }: PreviewValidationProps) {
  const mockValidation = {
    isValid: true,
    errors: [],
    warnings: [
      {
        type: "font",
        message: 'Font "Montserrat Bold" not available on target device',
      },
    ],
    checks: [
      { name: "Assets", status: "success" },
      { name: "Operations", status: "success" },
      { name: "Audio", status: "success" },
      { name: "Fonts", status: "warning" },
      { name: "Overlays", status: "success" },
    ],
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="flex-1 border-b border-slate-800 p-4 space-y-4 overflow-y-auto"
    >
      <div>
        <h3 className="text-sm font-semibold text-slate-300 mb-3">
          Validation
        </h3>

        {/* Overall status */}
        <div className="flex items-center gap-2 mb-4">
          <CheckCircle
            size={20}
            className={
              mockValidation.isValid ? "text-green-400" : "text-red-400"
            }
          />
          <span className="text-sm text-slate-300">
            {mockValidation.isValid ? "Ready to render" : "Issues found"}
          </span>
        </div>

        {/* Checks */}
        <div className="space-y-2">
          {mockValidation.checks.map((check) => (
            <motion.div
              key={check.name}
              whileHover={{ x: 4 }}
              className="flex items-center justify-between p-2 rounded-lg bg-slate-800/50 border border-slate-700/50"
            >
              <span className="text-xs text-slate-300">{check.name}</span>
              <div className="flex items-center gap-2">
                {check.status === "success" && (
                  <CheckCircle size={14} className="text-green-400" />
                )}
                {check.status === "warning" && (
                  <AlertTriangle size={14} className="text-yellow-400" />
                )}
                {check.status === "error" && (
                  <AlertCircle size={14} className="text-red-400" />
                )}
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Warnings */}
      {mockValidation.warnings.length > 0 && (
        <motion.div
          className="p-3 rounded-lg bg-yellow-900/30 border border-yellow-700/50"
          whileHover={{ borderColor: "#fbbf24" }}
        >
          <p className="text-xs font-semibold text-yellow-300 mb-2 flex items-center gap-2">
            <AlertTriangle size={14} />
            Warnings ({mockValidation.warnings.length})
          </p>
          <div className="space-y-1">
            {mockValidation.warnings.map((warning, idx) => (
              <p key={idx} className="text-xs text-yellow-200">
                {warning.message}
              </p>
            ))}
          </div>
        </motion.div>
      )}

      {/* Errors */}
      {mockValidation.errors.length > 0 && (
        <motion.div
          className="p-3 rounded-lg bg-red-900/30 border border-red-700/50"
          whileHover={{ borderColor: "#ef4444" }}
        >
          <p className="text-xs font-semibold text-red-300 mb-2 flex items-center gap-2">
            <AlertCircle size={14} />
            Errors ({mockValidation.errors.length})
          </p>
          <div className="space-y-1">
            {mockValidation.errors.map((error, idx) => (
              <p key={idx} className="text-xs text-red-200">
                {error.message}
              </p>
            ))}
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}
