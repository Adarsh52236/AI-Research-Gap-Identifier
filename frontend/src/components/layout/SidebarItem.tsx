import { NavLink } from 'react-router-dom';
import { LucideIcon } from 'lucide-react';

interface SidebarItemProps {
  title: string;
  path: string;
  icon: LucideIcon;
  onClick?: () => void;
}

export function SidebarItem({ title, path, icon: Icon, onClick }: SidebarItemProps) {
  return (
    <NavLink
      to={path}
      onClick={onClick}
      className={({ isActive }) =>
        `group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
          isActive
            ? 'bg-primary/10 text-primary'
            : 'text-muted hover:bg-surface hover:text-text'
        }`
      }
    >
      <Icon
        className="mr-3 flex-shrink-0 h-5 w-5"
        aria-hidden="true"
      />
      <span className="truncate">{title}</span>
    </NavLink>
  );
}
