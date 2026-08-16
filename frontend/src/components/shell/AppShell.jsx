import React, { useEffect, useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import useAppStore from '../../store/useAppStore';
import AuthModal from '../auth/AuthModal';
import SettingsModal from './SettingsModal';
import Starfield from './Starfield';

export default function AppShell() {
  const { auth, ui, setUI } = useAppStore();
  const [authModalOpen, setAuthModalOpen] = useState(false);

  // Listen for open-auth event
  useEffect(() => {
    const handleOpenAuth = () => setAuthModalOpen(true);
    document.addEventListener('open-auth', handleOpenAuth);
    return () => document.removeEventListener('open-auth', handleOpenAuth);
  }, []);

  // Force auth modal if not logged in (optional strict mode)
  // For now, we just let it open on demand, or we can force it:
  useEffect(() => {
    if (!auth.user) {
      setAuthModalOpen(true);
    }
  }, [auth.user]);

  return (
    <div className="flex h-screen bg-bg text-text font-sans overflow-hidden relative">
      <Starfield />
      <Sidebar />
      <main className="flex-1 flex flex-col relative h-full max-w-full overflow-hidden">
        {/* Main content area restricted to max-w-3xl for readability */}
        <div className="flex-1 w-full mx-auto max-w-3xl h-full flex flex-col px-4 sm:px-6 relative">
          <Outlet />
        </div>
      </main>
      
      <AuthModal isOpen={authModalOpen} onClose={() => setAuthModalOpen(false)} />
      <SettingsModal isOpen={ui.isSettingsOpen} onClose={() => setUI({ isSettingsOpen: false })} />
    </div>
  );
}
