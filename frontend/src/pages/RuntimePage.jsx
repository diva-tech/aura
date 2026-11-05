import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function RuntimePage() {
  const [runtimeData, setRuntimeData] = useState(null);
  const [eventHistory, setEventHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRuntimeData = async () => {
      try {
        const response = await fetch('/api/runtime/status');
        const data = await response.json();
        setRuntimeData(data);
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch runtime data:', error);
        setLoading(false);
      }
    };

    fetchRuntimeData();
    const interval = setInterval(fetchRuntimeData, 2000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className="p-6">Loading runtime data...</div>;
  }

  if (!runtimeData) {
    return <div className="p-6">Failed to load runtime data</div>;
  }

  return (
    <div className="p-6 bg-slate-50 min-h-screen">
      <h1 className="text-3xl font-bold mb-6">AURA Runtime Status</h1>

      {/* System Status */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-sm font-semibold text-slate-500 uppercase">Status</h3>
          <p className="text-2xl font-bold text-green-600 mt-2">{runtimeData.status}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-sm font-semibold text-slate-500 uppercase">Version</h3>
          <p className="text-2xl font-bold text-blue-600 mt-2">{runtimeData.version}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-sm font-semibold text-slate-500 uppercase">Uptime</h3>
          <p className="text-2xl font-bold text-purple-600 mt-2">{Math.round(runtimeData.uptime_ms / 1000)}s</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-sm font-semibold text-slate-500 uppercase">Health</h3>
          <p className="text-2xl font-bold text-emerald-600 mt-2">Healthy</p>
        </div>
      </div>

      {/* Services Section */}
      <div className="bg-white rounded-lg shadow mb-6 p-6">
        <h2 className="text-xl font-bold mb-4">Registered Services</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-100">
              <tr>
                <th className="px-4 py-2 text-left">Service Name</th>
                <th className="px-4 py-2 text-left">Lifetime</th>
                <th className="px-4 py-2 text-left">Resolve Count</th>
                <th className="px-4 py-2 text-left">Status</th>
              </tr>
            </thead>
            <tbody>
              {runtimeData.services && Object.entries(runtimeData.services).map(([name, service]) => (
                <tr key={name} className="border-t">
                  <td className="px-4 py-2 font-mono text-sm">{name}</td>
                  <td className="px-4 py-2">{service.lifetime}</td>
                  <td className="px-4 py-2 text-right">{service.resolve_count || 0}</td>
                  <td className="px-4 py-2">
                    <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">Active</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Plugins Section */}
      <div className="bg-white rounded-lg shadow mb-6 p-6">
        <h2 className="text-xl font-bold mb-4">Loaded Plugins</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {runtimeData.plugins && Object.entries(runtimeData.plugins).map(([id, plugin]) => (
            <div key={id} className="border rounded-lg p-4">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h3 className="font-semibold">{plugin.name}</h3>
                  <p className="text-sm text-slate-500">{plugin.id}</p>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-semibold ${
                  plugin.status === 'initialized' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                }`}>
                  {plugin.status}
                </span>
              </div>
              <p className="text-sm text-slate-600 mb-2">{plugin.description}</p>
              <div className="text-xs text-slate-500 mb-2">
                <p>Version: {plugin.version} | Author: {plugin.author}</p>
              </div>
              {plugin.tags && (
                <div className="flex flex-wrap gap-1">
                  {plugin.tags.map(tag => (
                    <span key={tag} className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Agents Section */}
      <div className="bg-white rounded-lg shadow mb-6 p-6">
        <h2 className="text-xl font-bold mb-4">Registered Agents</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {runtimeData.agents && Object.entries(runtimeData.agents).map(([id, agent]) => (
            <div key={id} className="border rounded-lg p-4">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h3 className="font-semibold">{agent.name}</h3>
                  <p className="text-sm text-slate-500">{agent.id}</p>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-semibold ${
                  agent.status === 'ready' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {agent.status}
                </span>
              </div>
              <p className="text-sm text-slate-600 mb-2">{agent.description}</p>
              <div className="text-xs text-slate-500 mb-2">
                <p>Type: {agent.agent_type} | Version: {agent.version}</p>
                <p>Executions: {agent.execution_count || 0}</p>
              </div>
              {agent.tags && (
                <div className="flex flex-wrap gap-1">
                  {agent.tags.map(tag => (
                    <span key={tag} className="px-2 py-1 bg-purple-100 text-purple-700 rounded text-xs">
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Events Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold mb-4">Event Statistics</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-slate-50 p-4 rounded">
            <p className="text-sm font-semibold text-slate-500">Total Events Published</p>
            <p className="text-3xl font-bold text-slate-700 mt-1">
              {runtimeData.events?.total_events_published || 0}
            </p>
          </div>
          <div className="bg-slate-50 p-4 rounded">
            <p className="text-sm font-semibold text-slate-500">Active Subscribers</p>
            <p className="text-3xl font-bold text-slate-700 mt-1">
              {runtimeData.events?.active_subscribers || 0}
            </p>
          </div>
          <div className="bg-slate-50 p-4 rounded">
            <p className="text-sm font-semibold text-slate-500">Event Bus Uptime</p>
            <p className="text-3xl font-bold text-slate-700 mt-1">
              {Math.round((runtimeData.events?.uptime_ms || 0) / 1000)}s
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
