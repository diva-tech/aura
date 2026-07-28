import { useEffect, useState } from 'react';

export default function AIFrameworkPage() {
  const [frameworkData, setFrameworkData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFrameworkData = async () => {
      try {
        const response = await fetch('/api/v1/ai/framework/status');
        const data = await response.json();
        setFrameworkData(data);
        setLoading(false);
      } catch (error) {
        console.error('Failed to fetch framework data:', error);
        setLoading(false);
      }
    };

    fetchFrameworkData();
    const interval = setInterval(fetchFrameworkData, 3000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return <div className="p-6">Loading AI Framework data...</div>;
  }

  if (!frameworkData) {
    return <div className="p-6">Failed to load AI Framework data</div>;
  }

  return (
    <div className="p-6 bg-slate-50 min-h-screen">
      <h1 className="text-4xl font-bold mb-2">AURA AI Framework</h1>
      <p className="text-slate-600 mb-6">Provider-agnostic, architecture-first framework for AI agents</p>

      {/* Framework Health */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-sm font-semibold text-slate-500 uppercase">Framework Status</h3>
          <p className="text-2xl font-bold text-blue-600 mt-2">{frameworkData.status}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-sm font-semibold text-slate-500 uppercase">Agents</h3>
          <p className="text-2xl font-bold text-green-600 mt-2">{frameworkData.agent_count || 0}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-sm font-semibold text-slate-500 uppercase">Tools</h3>
          <p className="text-2xl font-bold text-purple-600 mt-2">{frameworkData.tool_count || 0}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="text-sm font-semibold text-slate-500 uppercase">Providers</h3>
          <p className="text-2xl font-bold text-orange-600 mt-2">{frameworkData.provider_count || 0}</p>
        </div>
      </div>

      {/* Registered Agents */}
      <div className="bg-white rounded-lg shadow mb-6 p-6">
        <h2 className="text-xl font-bold mb-4">Registered Agents</h2>
        {frameworkData.agents && frameworkData.agents.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {frameworkData.agents.map((agent) => (
              <div key={agent.id} className="border rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold">{agent.name}</h3>
                    <p className="text-sm text-slate-500 font-mono">{agent.id}</p>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${
                    agent.status === 'ready' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {agent.status}
                  </span>
                </div>
                <p className="text-sm text-slate-600 mt-2">{agent.description}</p>
                <div className="text-xs text-slate-500 mt-2">
                  <p>Type: {agent.agent_type} | Executions: {agent.execution_count || 0}</p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-slate-500">No agents registered yet</p>
        )}
      </div>

      {/* Registered Tools */}
      <div className="bg-white rounded-lg shadow mb-6 p-6">
        <h2 className="text-xl font-bold mb-4">Registered Tools</h2>
        {frameworkData.tools && frameworkData.tools.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {frameworkData.tools.map((tool) => (
              <div key={tool.id} className="border rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold">{tool.name}</h3>
                    <p className="text-sm text-slate-500 font-mono">{tool.id}</p>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${
                    tool.status === 'healthy' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {tool.status}
                  </span>
                </div>
                <p className="text-sm text-slate-600 mt-2">{tool.description}</p>
                <div className="mt-2">
                  {tool.capabilities && tool.capabilities.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {tool.capabilities.slice(0, 3).map((cap) => (
                        <span key={cap} className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">
                          {cap}
                        </span>
                      ))}
                      {tool.capabilities.length > 3 && (
                        <span className="px-2 py-1 text-xs text-slate-500">
                          +{tool.capabilities.length - 3} more
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-slate-500">No tools registered yet</p>
        )}
      </div>

      {/* Registered Providers */}
      <div className="bg-white rounded-lg shadow mb-6 p-6">
        <h2 className="text-xl font-bold mb-4">Registered Providers</h2>
        {frameworkData.providers && frameworkData.providers.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {frameworkData.providers.map((provider) => (
              <div key={provider.id} className="border rounded-lg p-4">
                <h3 className="font-semibold">{provider.type}</h3>
                <p className="text-sm text-slate-500 mt-1">{provider.description}</p>
                <span className={`inline-block mt-2 px-2 py-1 rounded text-xs font-semibold ${
                  provider.status === 'ready' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                }`}>
                  {provider.status}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-slate-500">No providers registered yet</p>
        )}
      </div>

      {/* Current Sessions */}
      <div className="bg-white rounded-lg shadow mb-6 p-6">
        <h2 className="text-xl font-bold mb-4">Current Sessions</h2>
        {frameworkData.sessions && frameworkData.sessions.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-100">
                <tr>
                  <th className="px-4 py-2 text-left">Session ID</th>
                  <th className="px-4 py-2 text-left">Agent</th>
                  <th className="px-4 py-2 text-left">Goal</th>
                  <th className="px-4 py-2 text-left">Status</th>
                </tr>
              </thead>
              <tbody>
                {frameworkData.sessions.map((session) => (
                  <tr key={session.id} className="border-t">
                    <td className="px-4 py-2 font-mono text-xs">{session.id.slice(0, 8)}...</td>
                    <td className="px-4 py-2">{session.agent_id}</td>
                    <td className="px-4 py-2">{session.goal_id}</td>
                    <td className="px-4 py-2">
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${
                        session.status === 'running' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                      }`}>
                        {session.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-slate-500">No active sessions</p>
        )}
      </div>

      {/* Current Goals */}
      <div className="bg-white rounded-lg shadow mb-6 p-6">
        <h2 className="text-xl font-bold mb-4">Current Goals</h2>
        {frameworkData.goals && frameworkData.goals.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {frameworkData.goals.map((goal) => (
              <div key={goal.id} className="border rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold">{goal.title}</h3>
                    <p className="text-sm text-slate-500 font-mono">{goal.id.slice(0, 8)}...</p>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${
                    goal.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'
                  }`}>
                    {goal.status}
                  </span>
                </div>
                <p className="text-sm text-slate-600 mt-2">{goal.objective}</p>
                <div className="text-xs text-slate-500 mt-2">
                  <p>Priority: {goal.priority}</p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-slate-500">No goals created yet</p>
        )}
      </div>

      {/* Framework Health */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold mb-4">Framework Health</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-slate-50 p-4 rounded">
            <p className="text-sm font-semibold text-slate-500">Memory Systems</p>
            <p className="text-sm text-slate-700 mt-2">{frameworkData.memory_status || 'Ready'}</p>
          </div>
          <div className="bg-slate-50 p-4 rounded">
            <p className="text-sm font-semibold text-slate-500">Planning System</p>
            <p className="text-sm text-slate-700 mt-2">{frameworkData.planning_status || 'Ready'}</p>
          </div>
          <div className="bg-slate-50 p-4 rounded">
            <p className="text-sm font-semibold text-slate-500">Execution Engine</p>
            <p className="text-sm text-slate-700 mt-2">{frameworkData.execution_status || 'Ready'}</p>
          </div>
          <div className="bg-slate-50 p-4 rounded">
            <p className="text-sm font-semibold text-slate-500">Event System</p>
            <p className="text-sm text-slate-700 mt-2">{frameworkData.event_status || 'Ready'}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
