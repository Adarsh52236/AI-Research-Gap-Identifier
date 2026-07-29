import { Bell, Search, Menu } from 'lucide-react';
import { useLocation } from 'react-router-dom';
import { ROUTES } from '@/app/router';

interface HeaderProps {
  onOpenSidebar: () => void;
}

export function Header({ onOpenSidebar }: HeaderProps) {
  const location = useLocation();
  
  // Find current route title from metadata
  const currentRoute = Object.values(ROUTES).find(route => route.path === location.pathname);
  const title = currentRoute?.title || 'ResearchOS';

  return (
    <header className="sticky top-0 z-10 flex h-16 flex-shrink-0 bg-surface border-b border-border">
      <button
        type="button"
        className="border-r border-border px-4 text-gray-500 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary md:hidden"
        onClick={onOpenSidebar}
      >
        <span className="sr-only">Open sidebar</span>
        <Menu className="h-6 w-6" aria-hidden="true" />
      </button>
      
      <div className="flex flex-1 justify-between px-4 sm:px-6 lg:px-8">
        <div className="flex flex-1 items-center">
          <h1 className="text-xl font-semibold text-text">{title}</h1>
        </div>
        <div className="ml-4 flex items-center md:ml-6 gap-4">
          <div className="relative hidden md:flex items-center text-muted focus-within:text-text">
            <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
              <Search className="h-5 w-5" aria-hidden="true" />
            </div>
            <input
              id="search-field"
              className="block h-9 w-full rounded-md border border-border bg-background py-2 pl-10 pr-3 text-sm placeholder-muted focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
              placeholder="Search..."
              type="search"
              name="search"
              disabled
            />
          </div>

          <button
            type="button"
            className="rounded-full bg-surface p-1 text-muted hover:text-text focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
          >
            <span className="sr-only">View notifications</span>
            <Bell className="h-6 w-6" aria-hidden="true" />
          </button>

          {/* Profile dropdown placeholder */}
          <div className="relative ml-3">
            <button className="flex max-w-xs items-center rounded-full bg-surface text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2">
              <span className="sr-only">Open user menu</span>
              <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold">
                U
              </div>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
