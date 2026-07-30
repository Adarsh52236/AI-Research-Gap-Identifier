import { createBrowserRouter } from 'react-router-dom';
import { 
  LayoutDashboard, 
  FolderKanban, 
  Sparkles, 
  Library as LibraryIcon, 
  FileBarChart, 
  Settings as SettingsIcon 
} from 'lucide-react';

// Components
import { AppLayout } from '@/components/layout/AppLayout';
import { Dashboard } from '@/pages/Dashboard';
import { ProjectsPage } from '@/features/projects/pages/ProjectsPage';
import { ProjectDetailPage } from '@/features/projects/pages/ProjectDetailPage';
import { Analysis } from '@/pages/Analysis';
import { AnalysisViewer } from '@/features/analysis/components/AnalysisViewer';
import { Reports } from '@/pages/Reports';
import { Library } from '@/pages/Library';
import { Settings } from '@/pages/Settings';
import { NotFound } from '@/pages/NotFound';

import { LoginPage } from '@/features/auth/pages/LoginPage';
import { RegisterPage } from '@/features/auth/pages/RegisterPage';
import { ProtectedRoute } from '@/features/auth/components/ProtectedRoute';
import { GuestRoute } from '@/features/auth/components/GuestRoute';

// Route Metadata Configuration
export const ROUTES = {
  DASHBOARD: {
    title: 'Dashboard',
    icon: LayoutDashboard,
    path: '/',
    component: Dashboard,
  },
  PROJECTS: {
    title: 'Projects',
    icon: FolderKanban,
    path: '/projects',
    component: ProjectsPage,
  },
  ANALYSIS: {
    title: 'Analysis',
    icon: Sparkles,
    path: '/analysis',
    component: Analysis,
  },
  LIBRARY: {
    title: 'Library',
    icon: LibraryIcon,
    path: '/library',
    component: Library,
  },
  REPORTS: {
    title: 'Reports',
    icon: FileBarChart,
    path: '/reports',
    component: Reports,
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
        element: <Dashboard />,
      },
      {
        path: ROUTES.PROJECTS.path,
        element: <ProjectsPage />,
      },
      {
        path: '/projects/:projectId',
        element: <ProjectDetailPage />,
      },
      {
        path: ROUTES.ANALYSIS.path,
        element: <Analysis />,
      },
      {
        path: '/analysis/:analysisId',
        element: <AnalysisViewer />,
      },
      {
        path: ROUTES.LIBRARY.path,
        element: <Library />,
      },
      {
        path: ROUTES.REPORTS.path,
        element: <Reports />,
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
