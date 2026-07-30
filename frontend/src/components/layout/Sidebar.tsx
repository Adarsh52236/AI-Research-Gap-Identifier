import { X, Plus, LogOut, Folder } from 'lucide-react';
import { SidebarItem } from './SidebarItem';
import { ROUTES } from '@/app/router';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { useProjectStore } from '@/features/projects/store/projectStore';
import { useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const { user, logout } = useAuth();
  const { projects, fetchProjects } = useProjectStore();
  const navigate = useNavigate();

  useEffect(() => {
    if (user) {
      fetchProjects();
    }
  }, [user, fetchProjects]);

  const userInitials = user?.full_name 
    ? user.full_name.substring(0, 2).toUpperCase() 
    : user?.username.substring(0, 2).toUpperCase() || 'U';

  return (
    <>
      {/* Mobile Drawer Overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-40 bg-gray-900/80 backdrop-blur-sm md:hidden" 
          onClick={onClose}
        />
      )}

      {/* Sidebar Content */}
      <div
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-sidebar text-white transform transition-transform duration-300 ease-in-out md:translate-x-0 md:static md:inset-0 flex flex-col ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* User Profile / Account Switcher */}
        <div className="flex items-center justify-between h-16 px-4 bg-sidebar border-b border-white/10">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="flex-shrink-0 h-8 w-8 rounded bg-primary/20 flex items-center justify-center text-primary font-bold text-sm">
              {userInitials}
            </div>
            <div className="truncate">
              <div className="text-sm font-medium text-white truncate">
                {user?.full_name || user?.username}
              </div>
              <div className="text-xs text-gray-400">ResearchOS</div>
            </div>
          </div>
          <button onClick={onClose} className="md:hidden text-gray-400 hover:text-white">
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* New Research Action */}
        <div className="p-4">
          <button
            onClick={() => {
              navigate('/');
              onClose();
            }}
            className="w-full flex items-center justify-center gap-2 bg-primary hover:bg-blue-600 text-white py-2 px-4 rounded-md font-medium transition-colors"
          >
            <Plus className="w-4 h-4" />
            New Research
          </button>
        </div>

        {/* Navigation */}
        <div className="flex-1 overflow-y-auto px-3 py-2 space-y-6">
          <div>
            <h3 className="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Main</h3>
            <div className="space-y-1">
              <SidebarItem {...ROUTES.DASHBOARD} onClick={onClose} />
            </div>
          </div>
          
          <div>
            <div className="flex items-center justify-between px-3 mb-2">
              <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Workspace</h3>
            </div>
            <div className="space-y-1">
              {projects.length === 0 ? (
                <div className="px-3 py-2 text-xs text-gray-500 italic">No projects yet</div>
              ) : (
                projects.map(project => (
                  <Link
                    key={project.id}
                    to={`/projects/${project.id}`}
                    onClick={onClose}
                    className="flex items-center px-3 py-2 text-sm font-medium rounded-md text-gray-300 hover:bg-gray-800 hover:text-white transition-colors group"
                  >
                    <Folder className="mr-3 h-4 w-4 text-gray-400 group-hover:text-gray-300" />
                    <span className="truncate">{project.name}</span>
                  </Link>
                ))
              )}
            </div>
          </div>

          <div>
            <h3 className="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">System</h3>
            <div className="space-y-1">
              <SidebarItem {...ROUTES.SETTINGS} onClick={onClose} />
            </div>
          </div>
        </div>

        {/* Footer / Logout */}
        <div className="p-4 border-t border-white/10">
          <button
            onClick={logout}
            className="w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md text-gray-400 hover:text-white hover:bg-gray-800 transition-colors"
          >
            <LogOut className="w-4 h-4" />
            Sign out
          </button>
        </div>
      </div>
    </>
  );
}

