import { X } from 'lucide-react';
import { SidebarItem } from './SidebarItem';
import { ROUTES } from '@/app/router';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
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
        className={`fixed inset-y-0 left-0 z-50 w-64 bg-sidebar text-white transform transition-transform duration-300 ease-in-out md:translate-x-0 md:static md:inset-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex items-center justify-between h-16 px-6 bg-sidebar border-b border-white/10">
          <span className="text-xl font-bold tracking-tight text-white">ResearchOS</span>
          <button onClick={onClose} className="md:hidden text-gray-400 hover:text-white">
            <X className="h-6 w-6" />
          </button>
        </div>

        <div className="flex-1 h-0 overflow-y-auto pt-5 pb-4">
          <nav className="px-3 space-y-8">
            <div>
              <h3 className="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Main</h3>
              <div className="space-y-1">
                <SidebarItem {...ROUTES.DASHBOARD} onClick={onClose} />
                <SidebarItem {...ROUTES.PROJECTS} onClick={onClose} />
                <SidebarItem {...ROUTES.ANALYSIS} onClick={onClose} />
              </div>
            </div>
            
            <div>
              <h3 className="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Workspace</h3>
              <div className="space-y-1">
                <SidebarItem {...ROUTES.LIBRARY} onClick={onClose} />
                <SidebarItem {...ROUTES.REPORTS} onClick={onClose} />
              </div>
            </div>

            <div>
              <h3 className="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">System</h3>
              <div className="space-y-1">
                <SidebarItem {...ROUTES.SETTINGS} onClick={onClose} />
              </div>
            </div>
          </nav>
        </div>
      </div>
    </>
  );
}
