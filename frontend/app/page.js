"use client";

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Play, RotateCcw, AlertTriangle, CheckCircle, Clock, Plus, Activity } from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Dashboard() {
  const [workflows, setWorkflows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [newWorkflowName, setNewWorkflowName] = useState('');
  const [simulateFailure, setSimulateFailure] = useState(false);

  const fetchWorkflows = async () => {
    try {
      const res = await axios.get(`${API_URL}/workflows?limit=20`);
      // Sort by creation date desc
      const sorted = res.data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      setWorkflows(sorted);
      setLoading(false);
    } catch (error) {
      console.error("Failed to fetch workflows", error);
    }
  };

  useEffect(() => {
    fetchWorkflows();
    const interval = setInterval(fetchWorkflows, 2000); // Live refresh every 2s
    return () => clearInterval(interval);
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!newWorkflowName) return;

    try {
      const payload = {
        name: newWorkflowName,
        tasks: [
          {
            name: "Data Ingestion",
            task_type: "HTTP_REQUEST",
            payload: { simulate_failure: false },
            next_task: "Processing",
            max_retries: 3
          },
          {
            name: "Processing",
            task_type: "COMPUTE",
            payload: { simulate_failure: simulateFailure },
            next_task: "Archival",
            max_retries: 3
          },
          {
            name: "Archival",
            task_type: "IO_OPERATION",
            payload: { simulate_failure: false },
            next_task: null,
            max_retries: 3
          }
        ]
      };

      await axios.post(`${API_URL}/workflows`, payload);
      setNewWorkflowName('');
      setSimulateFailure(false);
      setShowCreate(false);
      fetchWorkflows();
    } catch (error) {
      console.error("Failed to create workflow", error);
      alert("Failed to create workflow");
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'COMPLETED': return 'bg-green-100 text-green-800 border-green-200';
      case 'FAILED': return 'bg-red-100 text-red-800 border-red-200';
      case 'RUNNING': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'QUEUED': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'COMPLETED': return <CheckCircle size={16} />;
      case 'FAILED': return <AlertTriangle size={16} />;
      case 'RUNNING': return <Activity size={16} className="animate-spin-slow" />;
      case 'QUEUED': return <Clock size={16} />;
      default: return <Clock size={16} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans p-8">
      <div className="max-w-6xl mx-auto">

        {/* Header */}
        <header className="flex justify-between items-center mb-10">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-gray-900">Workflow Engine</h1>
            <p className="text-gray-500 mt-1">Self-healing distributed task orchestration</p>
          </div>
          <button
            onClick={() => setShowCreate(true)}
            className="flex items-center gap-2 bg-black text-white px-5 py-2.5 rounded-lg font-medium hover:bg-gray-800 transition-all shadow-sm"
          >
            <Plus size={18} />
            New Workflow
          </button>
        </header>

        {/* Create Modal (Inline for simplicity) */}
        {showCreate && (
          <div className="mb-8 bg-white p-6 rounded-xl shadow-lg border border-gray-100 animate-in fade-in slide-in-from-top-4">
            <h3 className="text-lg font-semibold mb-4">Create New Workflow</h3>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Workflow Name</label>
                <input
                  type="text"
                  value={newWorkflowName}
                  onChange={(e) => setNewWorkflowName(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-transparent outline-none transition-all"
                  placeholder="e.g., Monthly Report Generation"
                  autoFocus
                />
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="fail"
                  checked={simulateFailure}
                  onChange={(e) => setSimulateFailure(e.target.checked)}
                  className="w-4 h-4 text-black border-gray-300 rounded focus:ring-black"
                />
                <label htmlFor="fail" className="text-sm text-gray-700">Simulate Failure in 'Processing' task (Tests Auto-Healing)</label>
              </div>
              <div className="flex gap-3 pt-2">
                <button type="submit" className="bg-black text-white px-4 py-2 rounded-lg font-medium hover:bg-gray-800">
                  Launch Workflow
                </button>
                <button type="button" onClick={() => setShowCreate(false)} className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg font-medium hover:bg-gray-200">
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Workflow List */}
        <div className="grid gap-6">
          {loading ? (
            <div className="text-center py-20 text-gray-400">Loading workflows...</div>
          ) : workflows.length === 0 ? (
            <div className="text-center py-20 bg-white rounded-xl border border-dashed border-gray-300">
              <p className="text-gray-500">No workflows found. Create one to get started.</p>
            </div>
          ) : (
            workflows.map((wf) => (
              <div key={wf.id} className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden transition-all hover:shadow-md">
                <div className="p-6 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
                  <div className="flex items-center gap-4">
                    <div className={`p-2 rounded-full ${getStatusColor(wf.status)}`}>
                      {getStatusIcon(wf.status)}
                    </div>
                    <div>
                      <h3 className="font-semibold text-lg text-gray-900">{wf.name}</h3>
                      <p className="text-xs text-gray-500 font-mono mt-0.5">{wf.id}</p>
                    </div>
                  </div>
                  <div className={`px-3 py-1 rounded-full text-xs font-bold tracking-wider ${getStatusColor(wf.status)}`}>
                    {wf.status}
                  </div>
                </div>

                <div className="p-6 bg-white">
                  <div className="flex items-center relative">
                    {/* Connection Line */}
                    <div className="absolute top-1/2 left-0 w-full h-0.5 bg-gray-100 -z-10 transform -translate-y-1/2"></div>

                    {/* Tasks */}
                    <div className="flex justify-between w-full">
                      {wf.tasks.sort((a, b) => new Date(a.created_at) - new Date(b.created_at)).map((task, index) => (
                        <div key={task.id} className="flex flex-col items-center gap-2 group relative z-10 w-full">
                          <div className={`w-10 h-10 rounded-full flex items-center justify-center border-4 border-white shadow-sm transition-all ${getStatusColor(task.status).replace('bg-', 'bg-').replace('text-', 'text-')}`}>
                            {getStatusIcon(task.status)}
                          </div>
                          <div className="text-center">
                            <p className="font-medium text-sm text-gray-900">{task.name}</p>
                            <p className="text-xs text-gray-500">{task.task_type}</p>
                            {task.retry_count > 0 && (
                              <span className="inline-block mt-1 px-1.5 py-0.5 bg-orange-100 text-orange-700 text-[10px] rounded font-semibold">
                                Retry: {task.retry_count}
                              </span>
                            )}
                          </div>
                          {/* Failure Reason Tooltip */}
                          {task.error && (
                            <div className="absolute top-16 left-1/2 -translate-x-1/2 bg-red-800 text-white text-xs p-2 rounded max-w-[200px] opacity-0 group-hover:opacity-100 transition-opacity z-50 pointer-events-none">
                              {task.error}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

      </div>

      <style jsx global>{`
        @keyframes spin-slow {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .animate-spin-slow {
          animation: spin-slow 3s linear infinite;
        }
      `}</style>
    </div>
  );
}
