"use client";

import { motion } from "framer-motion";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const data = [
  { name: "Mon", views: 1200, subscribers: 5, watchTime: 40 },
  { name: "Tue", views: 1800, subscribers: 8, watchTime: 62 },
  { name: "Wed", views: 1400, subscribers: 3, watchTime: 48 },
  { name: "Thu", views: 2200, subscribers: 12, watchTime: 78 },
  { name: "Fri", views: 2800, subscribers: 18, watchTime: 95 },
  { name: "Sat", views: 2400, subscribers: 15, watchTime: 82 },
  { name: "Sun", views: 2100, subscribers: 10, watchTime: 70 },
];

export function HomePerformance({ projectId }: { projectId: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-6 rounded-lg border border-slate-700 bg-slate-800/30"
    >
      <h2 className="text-lg font-semibold text-white mb-4">
        This Week's Performance
      </h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#404854" />
          <XAxis dataKey="name" stroke="#94a3b8" />
          <YAxis stroke="#94a3b8" />
          <Tooltip
            contentStyle={{
              backgroundColor: "#1e293b",
              border: "1px solid #475569",
              borderRadius: "8px",
            }}
          />
          <Line
            type="monotone"
            dataKey="views"
            stroke="#3b82f6"
            strokeWidth={2}
          />
        </LineChart>
      </ResponsiveContainer>
    </motion.div>
  );
}
