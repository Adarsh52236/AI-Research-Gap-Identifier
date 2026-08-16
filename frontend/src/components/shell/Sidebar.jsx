import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import useAppStore from '../../store/useAppStore';
import { MessageSquare, Settings, Sun, Moon, Plus, FileText, ChevronLeft, ChevronRight } from 'lucide-react';
import clsx from 'clsx';

import ThemeToggle from './ThemeToggle';

export default function Sidebar() {
  const navigate = useNavigate();
  const { ui, setUI, runs, auth } = useAppStore();
  const collapsed = ui.sidebarCollapsed;

  const handleNewChat = () => {
    navigate('/app');
  };

  return (
    <div className={clsx(
      "flex flex-col h-screen border-r border-border bg-panel transition-all duration-200",
      collapsed ? "w-16" : "w-64"
    )}>
      {/* Brand & Toggle */}
      <div className="flex items-center justify-between p-4 border-b border-border">
        {!collapsed && <span className="font-semibold text-text whitespace-nowrap overflow-hidden">GapFinder AI</span>}
        <button onClick={() => setUI({ sidebarCollapsed: !collapsed })} className="p-1 rounded-md hover:bg-border text-muted">
          {collapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
        </button>
      </div>

      {/* New Chat */}
      <div className="p-2">
        <button 
          onClick={handleNewChat}
          className="flex items-center justify-center w-full gap-2 p-2 rounded-xl bg-accent text-white hover:opacity-90 transition-opacity"
          title="New Chat"
        >
          <Plus size={20} />
          {!collapsed && <span>New Chat</span>}
        </button>
      </div>

      {/* Review PDF */}
      <div className="px-2 pb-2 border-b border-border">
        <NavLink 
          to="/app/review"
          className={({ isActive }) => clsx(
            "flex items-center justify-center w-full gap-2 p-2 rounded-xl transition-colors",
            isActive ? "bg-accent/20 text-accent" : "bg-transparent text-text hover:bg-border",
            collapsed && "px-0"
          )}
          title="Review PDF"
        >
          <FileText size={20} />
          {!collapsed && <span>Review PDF</span>}
        </NavLink>
      </div>

      {/* History */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {!collapsed && <div className="text-xs font-medium text-muted px-2 py-2 uppercase tracking-wider">Recent</div>}
        {runs.map((run) => (
          <NavLink
            key={run.run_id}
            to={`/app/run/${run.run_id}`}
            className={({ isActive }) => clsx(
              "flex items-center gap-2 p-2 rounded-lg text-sm transition-colors",
              isActive ? "bg-accentSoft text-accent" : "text-muted hover:bg-border hover:text-text"
            )}
            title={run.query}
          >
            <MessageSquare size={18} className="shrink-0" />
            {!collapsed && <span className="truncate">{run.query || "Untitled Analysis"}</span>}
          </NavLink>
        ))}
      </div>

      {/* Bottom Actions */}
      <div className="p-2 border-t border-border flex flex-col gap-1">
        <ThemeToggle collapsed={collapsed} />
        {auth.user ? (
          <button 
            onClick={() => useAppStore.getState().logout()}
            className="flex items-center gap-2 p-2 rounded-lg text-sm text-muted hover:bg-border hover:text-text transition-colors"
            title="Log out"
          >
            <Settings size={18} />
            {!collapsed && <span>Log out ({auth.user.username})</span>}
          </button>
        ) : (
          <button 
            onClick={() => document.dispatchEvent(new CustomEvent('open-auth'))}
            className="flex items-center gap-2 p-2 rounded-lg text-sm text-muted hover:bg-border hover:text-text transition-colors"
            title="Log in"
          >
            <Settings size={18} />
            {!collapsed && <span>Log in</span>}
          </button>
        )}
      </div>
    </div>
  );
}
