"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Settings,
  Trash2,
  ToggleRight,
  ToggleLeft,
  Info,
  AlertCircle,
} from "lucide-react";

interface InstalledPlugin {
  id: string;
  name: string;
  version: string;
  author: string;
  description: string;
  enabled: boolean;
  installedAt: string;
  permissions: string[];
  hasSettings: boolean;
}

interface PluginManagerProps {
  plugins: InstalledPlugin[];
  isLoading?: boolean;
  onEnable?: (pluginId: string) => void;
  onDisable?: (pluginId: string) => void;
  onUninstall?: (pluginId: string) => void;
  onSettings?: (pluginId: string) => void;
}

export function PluginManager({
  plugins,
  isLoading,
  onEnable,
  onDisable,
  onUninstall,
  onSettings,
}: PluginManagerProps) {
  const [selectedPlugin, setSelectedPlugin] = useState<string | null>(null);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold text-white">Installed Plugins</h1>
        <p className="text-slate-400">
          Manage and configure your installed extensions
        </p>
      </div>

      {/* Plugin List */}
      <div className="space-y-3">
        {plugins.length === 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="p-8 text-center rounded-lg border border-slate-700 bg-slate-800/20"
          >
            <Info size={32} className="mx-auto mb-3 text-slate-500" />
            <p className="text-slate-400 mb-1">No plugins installed</p>
            <p className="text-sm text-slate-500">
              Browse the marketplace to find and install plugins
            </p>
          </motion.div>
        ) : (
          plugins.map((plugin, idx) => (
            <motion.div
              key={plugin.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.05 }}
              className="p-5 rounded-lg border border-slate-700 bg-slate-800/30"
            >
              <div className="flex items-start justify-between gap-4">
                {/* Plugin Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="font-semibold text-white">{plugin.name}</h3>
                    <span className="px-2 py-1 rounded-full text-xs bg-slate-700 text-slate-300">
                      v{plugin.version}
                    </span>
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${
                        plugin.enabled
                          ? "bg-green-500/20 text-green-300"
                          : "bg-slate-700 text-slate-400"
                      }`}
                    >
                      {plugin.enabled ? "Enabled" : "Disabled"}
                    </span>
                  </div>
                  <p className="text-sm text-slate-400 mb-2">
                    {plugin.description}
                  </p>
                  <div className="flex items-center gap-4 text-xs text-slate-500">
                    <span>by {plugin.author}</span>
                    <span>installed {plugin.installedAt}</span>
                  </div>

                  {/* Permissions */}
                  {plugin.permissions.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-slate-700">
                      <p className="text-xs font-medium text-slate-400 mb-2">
                        Permissions
                      </p>
                      <div className="flex flex-wrap gap-1">
                        {plugin.permissions.map((perm) => (
                          <span
                            key={perm}
                            className="px-2 py-1 rounded text-xs bg-slate-900/50 text-slate-300"
                          >
                            {perm}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 flex-shrink-0">
                  {/* Toggle */}
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() =>
                      plugin.enabled
                        ? onDisable?.(plugin.id)
                        : onEnable?.(plugin.id)
                    }
                    className="p-2 rounded-lg hover:bg-slate-700 transition-colors"
                    title={plugin.enabled ? "Disable plugin" : "Enable plugin"}
                  >
                    {plugin.enabled ? (
                      <ToggleRight size={20} className="text-green-400" />
                    ) : (
                      <ToggleLeft size={20} className="text-slate-500" />
                    )}
                  </motion.button>

                  {/* Settings */}
                  {plugin.hasSettings && (
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => onSettings?.(plugin.id)}
                      className="p-2 rounded-lg hover:bg-slate-700 transition-colors"
                      title="Plugin settings"
                    >
                      <Settings size={20} className="text-blue-400" />
                    </motion.button>
                  )}

                  {/* Uninstall */}
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => {
                      if (
                        window.confirm(
                          `Uninstall ${plugin.name}? This cannot be undone.`
                        )
                      ) {
                        onUninstall?.(plugin.id);
                      }
                    }}
                    className="p-2 rounded-lg hover:bg-red-900/20 transition-colors"
                    title="Uninstall plugin"
                  >
                    <Trash2 size={20} className="text-red-400" />
                  </motion.button>
                </div>
              </div>

              {/* Expand for more details */}
              <AnimatePresence>
                {selectedPlugin === plugin.id && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="mt-4 pt-4 border-t border-slate-700 space-y-3"
                  >
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-slate-400 mb-1">Status</p>
                        <p className="text-white font-medium">
                          {plugin.enabled ? "Active" : "Inactive"}
                        </p>
                      </div>
                      <div>
                        <p className="text-slate-400 mb-1">Version</p>
                        <p className="text-white font-medium">
                          {plugin.version}
                        </p>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          ))
        )}
      </div>

      {/* Security Notice */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="p-4 rounded-lg border border-amber-700/50 bg-amber-950/20 flex gap-3"
      >
        <AlertCircle
          size={18}
          className="text-amber-400 flex-shrink-0 mt-0.5"
        />
        <div>
          <p className="text-sm font-medium text-amber-300 mb-1">
            Plugin Security
          </p>
          <p className="text-xs text-amber-200">
            Only install plugins from trusted sources. Plugins run with the
            permissions granted during installation.
          </p>
        </div>
      </motion.div>
    </motion.div>
  );
}
