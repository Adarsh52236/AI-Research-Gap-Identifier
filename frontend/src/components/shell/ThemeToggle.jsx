import React from 'react';
import useAppStore from '../../store/useAppStore';
import './ThemeToggle.css';

export default function ThemeToggle({ collapsed }) {
  const { ui, setUI } = useAppStore();
  const isDark = ui.theme === 'dark';

  const toggleTheme = () => {
    const newTheme = isDark ? 'light' : 'dark';
    setUI({ theme: newTheme });
    document.documentElement.classList.toggle('dark', newTheme === 'dark');
  };

  return (
    <div className={`flex items-center gap-3 p-2 rounded-lg text-sm text-muted hover:bg-border transition-colors ${collapsed ? 'justify-center' : ''}`} title="Toggle Theme">
      <div 
        className="toggle-switch shrink-0" 
        style={{ transform: 'scale(0.5)', transformOrigin: collapsed ? 'center center' : 'left center', margin: '-12px 0', width: collapsed ? '50px' : '100px' }}
      >
        <label className="switch-label">
          <input 
            type="checkbox" 
            className="checkbox" 
            checked={!isDark} 
            onChange={toggleTheme} 
          />
          <span className="slider"></span>
        </label>
      </div>
      {!collapsed && <span>{isDark ? 'Dark Mode' : 'Light Mode'}</span>}
    </div>
  );
}
