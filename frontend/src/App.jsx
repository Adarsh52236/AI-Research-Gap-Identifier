import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Landing from './pages/Landing';
import ChatDashboard from './pages/ChatDashboard';
import ReviewDashboard from './pages/ReviewDashboard';
import AppShell from './components/shell/AppShell';
import { runsService } from './services/runsService';
import useAppStore from './store/useAppStore';

export default function App() {
  const { setRuns, auth } = useAppStore();

  // Load history when auth token changes
  useEffect(() => {
    async function loadHistory() {
      if (!auth.token) return;
      try {
        const history = await runsService.listRuns();
        setRuns(history);
      } catch (e) {
        console.error("Failed to load history", e);
      }
    }
    loadHistory();
  }, [auth.token]);

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/app" element={<AppShell />}>
          <Route index element={<ChatDashboard />} />
          <Route path="run/:runId" element={<ChatDashboard />} />
          <Route path="review" element={<ReviewDashboard />} />
        </Route>
      </Routes>
    </Router>
  );
}
