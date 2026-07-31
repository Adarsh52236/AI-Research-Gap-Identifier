import { X, Plus, LogOut, MessageSquare } from 'lucide-react';
import { SidebarItem } from './SidebarItem';
import { ROUTES } from '@/app/router';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { useChatStore } from '@/features/chat/store/chatStore';
import { useEffect } from 'react';
import { useNavigate, Link, useParams } from 'react-router-dom';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const { user, logout } = useAuth();
  const { sessions, fetchSessions } = useChatStore();
  const navigate = useNavigate();
  const { id } = useParams();

  useEffect(() => {
    if (user) {
      fetchSessions();
    }
  }, [user, fetchSessions]);

  const userInitials = user?.full_name 
    ? user.full_name.substring(0, 2).toUpperCase() 
    : user?.username.substring(0, 2).toUpperCase() || 'U';

  return (
    <>
      {/* Mobile Drawer Overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-40 bg-gray-900/40 backdrop-blur-sm md:hidden" 
          onClick={onClose}
        />
      )}

      {/* Sidebar Content */}
      <div
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-sidebar text-text border-r border-border transform transition-transform duration-300 ease-in-out md:translate-x-0 md:static md:inset-0 flex flex-col ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Header / New Research Action */}
        <div className="p-3 flex items-center justify-between">
          <button
            onClick={() => {
              navigate('/');
              onClose();
            }}
            className="flex-1 flex items-center gap-2 bg-transparent hover:bg-gray-100 text-text py-2 px-3 rounded-lg font-medium transition-colors border border-border mr-2"
          >
            <Plus className="w-4 h-4 text-primary" />
            <span className="text-sm">New Research</span>
          </button>
          <button onClick={onClose} className="md:hidden text-muted hover:text-text p-2">
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation */}
        <div className="flex-1 overflow-y-auto px-3 py-2 space-y-6">
          {/* Recent Research */}
          <div>
            <h3 className="px-2 text-xs font-semibold text-muted mb-1 mt-2">Recent Research</h3>
            <div className="space-y-1">
              {sessions.length === 0 ? (
                <div className="px-3 py-2 text-xs text-muted italic">No recent research</div>
              ) : (
                sessions.map(session => (
                  <Link
                    key={session.id}
                    to={`/c/${session.id}`}
                    onClick={onClose}
                    className={`flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors group ${
                        id === session.id 
                        ? 'bg-gray-100 text-text' 
                        : 'text-muted hover:bg-gray-100 hover:text-text'
                    }`}
                  >
                    <span className="truncate">{session.title}</span>
                  </Link>
                ))
              )}
            </div>
          </div>

          {/* Library (Placeholders for now) */}
          <div>
            <h3 className="px-2 text-xs font-semibold text-muted mb-1">Library</h3>
            <div className="space-y-1">
              <button className="w-full flex items-center px-3 py-2 text-sm font-medium rounded-lg text-muted hover:bg-gray-100 hover:text-text transition-colors opacity-60 cursor-not-allowed">
                Uploaded Documents
              </button>
              <button className="w-full flex items-center px-3 py-2 text-sm font-medium rounded-lg text-muted hover:bg-gray-100 hover:text-text transition-colors opacity-60 cursor-not-allowed">
                Saved Reports
              </button>
              <SidebarItem {...ROUTES.SETTINGS} onClick={onClose} />
            </div>
          </div>
        </div>

        {/* User Profile / Logout */}
        <div className="p-3 mt-auto">
          <div className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors group cursor-pointer" onClick={logout}>
            <div className="flex-shrink-0 h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold text-sm">
              {userInitials}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-text truncate">
                {user?.full_name || user?.username}
              </div>
            </div>
            <LogOut className="w-4 h-4 text-muted opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
        </div>
      </div>
    </>
  );
}
