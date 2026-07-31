import { useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Menu, Settings } from 'lucide-react';
import { useChatStore } from '@/features/chat/store/chatStore';

export function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { currentSession, sessions } = useChatStore();
  const navigate = useNavigate();

  const activeSessionTitle = sessions.find(s => s.id === currentSession)?.title || 'New Analysis';

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      
      <div className="flex flex-col flex-1 w-0 overflow-hidden">
        <div className="sticky top-0 z-10 flex h-14 flex-shrink-0 bg-background/80 backdrop-blur-md border-b border-border items-center px-4 justify-between transition-colors">
          <div className="flex items-center">
            <button
              type="button"
              className="md:hidden text-muted hover:text-text focus:outline-none mr-4"
              onClick={() => setSidebarOpen(true)}
            >
              <span className="sr-only">Open sidebar</span>
              <Menu className="h-5 w-5" aria-hidden="true" />
            </button>
            <span className="text-sm font-semibold text-text truncate max-w-[200px] sm:max-w-md">
              {activeSessionTitle}
            </span>
          </div>
        </div>
        
        <main className="flex-1 relative z-0 overflow-y-auto focus:outline-none">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

