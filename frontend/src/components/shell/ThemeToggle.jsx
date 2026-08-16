import React from 'react';
import useAppStore from '../../store/useAppStore';
import './ThemeToggle.css';

export default function ThemeToggle() {
  const { ui, setUI } = useAppStore();
  const isDark = ui.theme === 'dark';

  const toggleTheme = () => {
    const newTheme = isDark ? 'light' : 'dark';
    setUI({ theme: newTheme });
    document.documentElement.classList.toggle('dark', newTheme === 'dark');
  };

  return (
    <div title="Toggle Theme">
      <div className="toggle-switch shadow-md rounded-full">
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
    </div>
  );
}
