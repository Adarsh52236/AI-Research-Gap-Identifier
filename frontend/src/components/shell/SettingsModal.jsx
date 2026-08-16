import React, { useState } from 'react';
import { X, Search, Trash2, User, Clock, AlertTriangle } from 'lucide-react';
import useAppStore from '../../store/useAppStore';
import { runsService } from '../../services/runsService';

export default function SettingsModal({ isOpen, onClose }) {
  const [activeTab, setActiveTab] = useState('profile');
  const [searchQuery, setSearchQuery] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);
  
  const { auth, logout, runs, removeRun, clearRuns } = useAppStore();

  if (!isOpen) return null;

  const filteredRuns = runs.filter(run => 
    (run.query || "Untitled Analysis").toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleDeleteRun = async (runId) => {
    try {
      setIsDeleting(true);
      await runsService.deleteRun(runId);
      removeRun(runId);
    } catch (err) {
      console.error("Failed to delete run:", err);
      alert("Failed to delete run");
    } finally {
      setIsDeleting(false);
    }
  };

  const handleClearAll = async () => {
    if (!window.confirm("Are you sure you want to permanently delete all history?")) return;
    try {
      setIsDeleting(true);
      await runsService.clearAllRuns();
      clearRuns();
    } catch (err) {
      console.error("Failed to clear history:", err);
      alert("Failed to clear history");
    } finally {
      setIsDeleting(false);
    }
  };

  const handleLogout = () => {
    logout();
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="w-full max-w-2xl bg-panel border border-border rounded-2xl shadow-xl overflow-hidden flex flex-col h-[80vh] max-h-[600px]">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border">
          <h2 className="text-xl font-semibold text-text">Settings</h2>
          <button 
            onClick={onClose}
            className="p-2 text-muted hover:text-text rounded-lg hover:bg-border transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        <div className="flex flex-1 overflow-hidden">
          {/* Tabs Sidebar */}
          <div className="w-48 border-r border-border p-4 space-y-2">
            <button
              onClick={() => setActiveTab('profile')}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === 'profile' 
                  ? 'bg-accent/20 text-accent' 
                  : 'text-muted hover:bg-border hover:text-text'
              }`}
            >
              <User size={18} />
              Profile
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                activeTab === 'history' 
                  ? 'bg-accent/20 text-accent' 
                  : 'text-muted hover:bg-border hover:text-text'
              }`}
            >
              <Clock size={18} />
              History
            </button>
          </div>

          {/* Content Area */}
          <div className="flex-1 p-6 overflow-y-auto">
            {activeTab === 'profile' && (
              <div className="space-y-6">
                <h3 className="text-lg font-medium text-text">Profile Information</h3>
                
                <div className="p-4 bg-bg border border-border rounded-xl">
                  <p className="text-sm text-muted mb-1">Username</p>
                  <p className="text-text font-medium">{auth.user?.username || 'Guest'}</p>
                  
                  {auth.user?.email && (
                    <>
                      <p className="text-sm text-muted mt-4 mb-1">Email</p>
                      <p className="text-text font-medium">{auth.user.email}</p>
                    </>
                  )}
                </div>

                <div className="pt-4 border-t border-border">
                  <button 
                    onClick={handleLogout}
                    className="px-4 py-2 bg-red-900/20 text-red-400 border border-red-500/50 rounded-lg hover:bg-red-900/40 transition-colors font-medium text-sm"
                  >
                    Log Out
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'history' && (
              <div className="flex flex-col h-full">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg font-medium text-text">Research History</h3>
                  {runs.length > 0 && (
                    <button 
                      onClick={handleClearAll}
                      disabled={isDeleting}
                      className="text-sm text-red-400 hover:text-red-300 flex items-center gap-2 disabled:opacity-50"
                    >
                      <Trash2 size={16} />
                      Clear All
                    </button>
                  )}
                </div>

                <div className="relative mb-4">
                  <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
                  <input 
                    type="text" 
                    placeholder="Search history..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-9 pr-4 py-2 bg-bg border border-border rounded-lg text-sm text-text focus:outline-none focus:border-accent"
                  />
                </div>

                <div className="flex-1 overflow-y-auto space-y-2 min-h-0 pr-2">
                  {filteredRuns.length === 0 ? (
                    <div className="text-center py-8 text-muted text-sm flex flex-col items-center">
                      <Clock size={32} className="mb-2 opacity-20" />
                      No history found.
                    </div>
                  ) : (
                    filteredRuns.map((run) => (
                      <div key={run.run_id} className="flex items-center justify-between p-3 bg-bg border border-border rounded-lg group">
                        <div className="flex-1 min-w-0 pr-4">
                          <p className="text-sm text-text truncate font-medium">
                            {run.query || "Untitled Analysis"}
                          </p>
                          <p className="text-xs text-muted mt-1">
                            {new Date(run.started_at).toLocaleString()}
                          </p>
                        </div>
                        <button 
                          onClick={() => handleDeleteRun(run.run_id)}
                          disabled={isDeleting}
                          className="p-2 text-muted hover:text-red-400 hover:bg-red-900/20 rounded-md opacity-0 group-hover:opacity-100 transition-all disabled:opacity-50"
                          title="Delete run"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
