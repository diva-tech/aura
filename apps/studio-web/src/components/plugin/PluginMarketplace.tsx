"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  Download,
  Star,
  Search,
  Filter,
  Loader2,
  CheckCircle,
} from "lucide-react";

interface PluginListing {
  id: string;
  name: string;
  author: string;
  description: string;
  icon: string;
  downloads: number;
  rating: number;
  totalRatings: number;
  category: string;
  verified: boolean;
  featured: boolean;
  version: string;
  installed?: boolean;
}

interface PluginMarketplaceProps {
  plugins: PluginListing[];
  isLoading?: boolean;
  onInstall?: (pluginId: string) => void;
  onSearch?: (query: string) => void;
  selectedCategory?: string;
  onCategoryChange?: (category: string) => void;
}

const categories = [
  { id: "all", label: "All" },
  { id: "video_editing", label: "Video Editing" },
  { id: "ai_models", label: "AI Models" },
  { id: "publishing", label: "Publishing" },
  { id: "analytics", label: "Analytics" },
  { id: "effects", label: "Effects" },
];

export function PluginMarketplace({
  plugins,
  isLoading,
  onInstall,
  onSearch,
  selectedCategory = "all",
  onCategoryChange,
}: PluginMarketplaceProps) {
  const [searchQuery, setSearchQuery] = useState("");

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="space-y-4">
        <h1 className="text-3xl font-bold text-white">Plugin Marketplace</h1>
        <p className="text-slate-400">
          Extend AURA Studio with community-built plugins
        </p>
      </div>

      {/* Search & Filter */}
      <div className="space-y-4">
        <div className="relative">
          <Search size={20} className="absolute left-3 top-3 text-slate-500" />
          <input
            type="text"
            placeholder="Search plugins..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              onSearch?.(e.target.value);
            }}
            className="w-full pl-10 pr-4 py-2 rounded-lg bg-slate-800 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </div>

        {/* Categories */}
        <div className="flex gap-2 overflow-x-auto pb-2">
          {categories.map((cat) => (
            <motion.button
              key={cat.id}
              whileHover={{ scale: 1.05 }}
              onClick={() => onCategoryChange?.(cat.id)}
              className={`px-4 py-2 rounded-lg font-medium transition-all whitespace-nowrap ${
                selectedCategory === cat.id
                  ? "bg-blue-600 text-white"
                  : "bg-slate-800 text-slate-300 hover:bg-slate-700"
              }`}
            >
              {cat.label}
            </motion.button>
          ))}
        </div>
      </div>

      {/* Plugin Grid */}
      {isLoading ? (
        <div className="flex justify-center py-12">
          <Loader2 size={32} className="text-blue-400 animate-spin" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {plugins.map((plugin, idx) => (
            <motion.div
              key={plugin.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.05 }}
              className="p-5 rounded-lg border border-slate-700 bg-slate-800/30 hover:bg-slate-800/50 transition-all group"
            >
              {/* Featured Badge */}
              {plugin.featured && (
                <div className="mb-3 inline-block px-2 py-1 rounded-full bg-amber-500/20 border border-amber-500/50">
                  <p className="text-xs font-medium text-amber-300">Featured</p>
                </div>
              )}

              {/* Icon & Name */}
              <div className="flex gap-3 mb-3">
                <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
                  <span className="text-xl font-bold text-white">
                    {plugin.name[0].toUpperCase()}
                  </span>
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-white">{plugin.name}</h3>
                  <p className="text-xs text-slate-500">{plugin.author}</p>
                </div>
                {plugin.verified && (
                  <CheckCircle size={18} className="text-green-400" />
                )}
              </div>

              {/* Description */}
              <p className="text-sm text-slate-300 mb-4 line-clamp-2">
                {plugin.description}
              </p>

              {/* Rating */}
              <div className="flex items-center gap-2 mb-4">
                <div className="flex items-center gap-1">
                  {[...Array(5)].map((_, i) => (
                    <Star
                      key={i}
                      size={14}
                      className={
                        i < Math.floor(plugin.rating)
                          ? "fill-yellow-400 text-yellow-400"
                          : "text-slate-600"
                      }
                    />
                  ))}
                </div>
                <span className="text-xs text-slate-400">
                  {plugin.rating.toFixed(1)} ({plugin.totalRatings})
                </span>
              </div>

              {/* Footer */}
              <div className="flex items-center justify-between pt-4 border-t border-slate-700">
                <div className="flex items-center gap-1 text-xs text-slate-500">
                  <Download size={14} />
                  {(plugin.downloads / 1000).toFixed(1)}k downloads
                </div>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => onInstall?.(plugin.id)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    plugin.installed
                      ? "bg-green-500/20 text-green-300 border border-green-500/50"
                      : "bg-blue-600 text-white hover:bg-blue-700"
                  }`}
                >
                  {plugin.installed ? "Installed" : "Install"}
                </motion.button>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {!isLoading && plugins.length === 0 && (
        <div className="text-center py-12">
          <p className="text-slate-400 mb-2">No plugins found</p>
          <p className="text-sm text-slate-500">
            Try a different search or category
          </p>
        </div>
      )}
    </motion.div>
  );
}
