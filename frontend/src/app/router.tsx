import { createBrowserRouter } from 'react-router-dom';
import { 
  MessageSquare,
  Settings as SettingsIcon 
} from 'lucide-react';

// Components
import { AppLayout } from '@/components/layout/AppLayout';
import { Settings } from '@/pages/Settings';
import { NotFound } from '@/pages/NotFound';
import { ChatInterface } from '@/features/chat/components/ChatInterface';

import { LoginPage } from '@/features/auth/pages/LoginPage';
import { RegisterPage } from '@/features/auth/pages/RegisterPage';
import { ProtectedRoute } from '@/features/auth/components/ProtectedRoute';
import { GuestRoute } from '@/features/auth/components/GuestRoute';

// Route Metadata Configuration
export const ROUTES = {
  DASHBOARD: {
    title: 'Chat',
    icon: MessageSquare,
    path: '/',
    component: ChatInterface,
  },
  SETTINGS: {
    title: 'Settings',
    icon: SettingsIcon,
    path: '/settings',
    component: Settings,
  },
} as const;

// Router Configuration
export const router = createBrowserRouter([
  {
    path: '/login',
    element: (
      <GuestRoute>
        <LoginPage />
      </GuestRoute>
    ),
  },
  {
    path: '/register',
    element: (
      <GuestRoute>
        <RegisterPage />
      </GuestRoute>
    ),
  },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <AppLayout />
      </ProtectedRoute>
    ),
    errorElement: <NotFound />,
    children: [
      {
        index: true,
        element: <ChatInterface />,
      },
      {
        path: '/c/:id',
        element: <ChatInterface />,
      },
      {
        path: ROUTES.SETTINGS.path,
        element: <Settings />,
      },
      {
        path: '*',
        element: <NotFound />,
      },
    ],
  },
]);
