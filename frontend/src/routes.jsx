import React from 'react';
import Landing from './pages/Landing';
import ChatDashboard from './pages/ChatDashboard';
import RunViewer from './pages/RunViewer';
import AppShell from './components/shell/AppShell';

export const routes = [
  { path: '/', element: <Landing /> },
  { 
    path: '/app', 
    element: <AppShell />,
    children: [
      { path: '', element: <ChatDashboard /> },
      { path: 'run/:runId', element: <RunViewer /> }
    ]
  }
];
