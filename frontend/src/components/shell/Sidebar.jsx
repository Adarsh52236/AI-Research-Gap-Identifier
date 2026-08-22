import React, { useEffect, useState, useRef } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import useAppStore from '../../store/useAppStore';
import useChatStore from '../../store/useChatStore';
import { MessageSquare, Settings, Plus, FileText, ChevronLeft, ChevronRight, MoreHorizontal, Edit2, Trash2, Check, X } from 'lucide-react';
import clsx from 'clsx';
import { isToday, isYesterday, subDays, isAfter } from 'date-fns';

export default function Sidebar() {
  const navigate = useNavigate();
  const { ui, setUI, auth } = useAppStore();
  const collapsed = ui.sidebarCollapsed;
  const { sessions, fetchSessions, activeSessionId, setActiveSessionId, updateSessionTitle, deleteSession } = useChatStore();
  
  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState("");
  const [menuOpenId, setMenuOpenId] = useState(null);
  const menuRef = useRef(null);

  useEffect(() => {
    if (auth.user) {
      fetchSessions();
    }
  }, [auth.user, fetchSessions]);

  useEffect(() => {
    // Close menu when clicking outside
    function handleClickOutside(event) {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setMenuOpenId(null);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleNewChat = () => {
    setActiveSessionId(null);
    navigate('/app');
  };

  const handleEditSubmit = (id) => {
    if (editTitle.trim()) {
      updateSessionTitle(id, editTitle.trim());
    }
    setEditingId(null);
  };

  const handleDelete = (id) => {
    if (window.confirm("Are you sure you want to delete this chat?")) {
      deleteSession(id);
      if (activeSessionId === id) {
        navigate('/app');
      }
    }
    setMenuOpenId(null);
  };

  // Grouping logic
  const now = new Date();
  const sevenDaysAgo = subDays(now, 7);
  const thirtyDaysAgo = subDays(now, 30);

  const groups = {
    Today: [],
    Yesterday: [],
    'Previous 7 Days': [],
    'Previous 30 Days': [],
    'Older': []
  };

  sessions.forEach(session => {
    const d = new Date(session.updated_at);
    if (isToday(d)) {
      groups.Today.push(session);
    } else if (isYesterday(d)) {
      groups.Yesterday.push(session);
    } else if (isAfter(d, sevenDaysAgo)) {
      groups['Previous 7 Days'].push(session);
    } else if (isAfter(d, thirtyDaysAgo)) {
      groups['Previous 30 Days'].push(session);
    } else {
      groups.Older.push(session);
    }
  });

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
      <div className="flex-1 overflow-y-auto p-2 space-y-4">
        {Object.entries(groups).map(([groupName, groupSessions]) => {
          if (groupSessions.length === 0) return null;
          return (
            <div key={groupName} className="space-y-1">
              {!collapsed && <div className="text-xs font-medium text-muted px-2 py-1 sticky top-0 bg-panel z-10">{groupName}</div>}
              {groupSessions.map((session) => (
                <div key={session.id} className="relative group flex items-center">
                   {editingId === session.id && !collapsed ? (
                     <div className="flex items-center gap-1 w-full p-1.5 rounded-lg border border-accent bg-bg">
                        <input 
                           type="text" 
                           autoFocus
                           className="flex-1 bg-transparent text-sm text-text outline-none px-1 min-w-0"
                           value={editTitle}
                           onChange={(e) => setEditTitle(e.target.value)}
                           onKeyDown={(e) => {
                             if (e.key === 'Enter') handleEditSubmit(session.id);
                             if (e.key === 'Escape') setEditingId(null);
                           }}
                        />
                        <button onClick={() => handleEditSubmit(session.id)} className="text-accent hover:bg-accent/20 p-1 rounded"><Check size={14}/></button>
                        <button onClick={() => setEditingId(null)} className="text-muted hover:bg-border p-1 rounded"><X size={14}/></button>
                     </div>
                   ) : (
                    <NavLink
                      to={`/app/chat/${session.id}`}
                      className={({ isActive }) => clsx(
                        "flex items-center gap-2 p-2 rounded-lg text-sm transition-colors flex-1 min-w-0",
                        isActive ? "bg-accentSoft text-accent pr-8" : "text-muted hover:bg-border hover:text-text pr-8",
                        collapsed && "justify-center pr-2"
                      )}
                      title={session.title}
                    >
                      <MessageSquare size={18} className="shrink-0" />
                      {!collapsed && <span className="truncate">{session.title}</span>}
                    </NavLink>
                   )}
                   
                   {!collapsed && editingId !== session.id && (
                     <div className={clsx(
                       "absolute right-1 top-1/2 -translate-y-1/2",
                       activeSessionId === session.id || menuOpenId === session.id ? "block" : "hidden group-hover:block"
                     )}>
                        <button 
                          onClick={(e) => {
                            e.preventDefault();
                            setMenuOpenId(menuOpenId === session.id ? null : session.id);
                          }}
                          className="p-1 rounded text-muted hover:text-text hover:bg-border/80"
                        >
                          <MoreHorizontal size={16} />
                        </button>
                        
                        {menuOpenId === session.id && (
                          <div ref={menuRef} className="absolute right-0 top-full mt-1 w-32 bg-popover border border-border rounded-lg shadow-lg z-50 py-1 overflow-hidden">
                            <button 
                              onClick={(e) => {
                                e.preventDefault();
                                setEditingId(session.id);
                                setEditTitle(session.title);
                                setMenuOpenId(null);
                              }}
                              className="w-full flex items-center gap-2 px-3 py-1.5 text-sm text-text hover:bg-border transition-colors text-left"
                            >
                              <Edit2 size={14} /> Rename
                            </button>
                            <button 
                              onClick={(e) => {
                                e.preventDefault();
                                handleDelete(session.id);
                              }}
                              className="w-full flex items-center gap-2 px-3 py-1.5 text-sm text-error hover:bg-error/10 transition-colors text-left"
                            >
                              <Trash2 size={14} /> Delete
                            </button>
                          </div>
                        )}
                     </div>
                   )}
                </div>
              ))}
            </div>
          );
        })}
      </div>

      {/* Bottom Actions */}
      <div className="p-2 border-t border-border flex flex-col gap-1">
        {auth.user ? (
          <button 
            onClick={() => setUI({ isSettingsOpen: true })}
            className="flex items-center gap-2 p-2 rounded-lg text-sm text-muted hover:bg-border hover:text-text transition-colors"
            title="Settings"
          >
            <Settings size={18} />
            {!collapsed && <span>Settings</span>}
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
