import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Landing from './pages/Landing';
import ChatDashboard from './pages/ChatDashboard';
import RunViewer from './pages/RunViewer';
import AppShell from './components/shell/AppShell';
import { runsService } from './services/runsService';
import useAppStore from './store/useAppStore';

export default function App() {
  const { setRuns } = useAppStore();

  // Load history on mount
  useEffect(() => {
    async function loadHistory() {
      try {
        const history = await runsService.listRuns();
        setRuns(history);
      } catch (e) {
        console.error("Failed to load history", e);
      }
    }
    loadHistory();
  }, []);

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/app" element={<AppShell />}>
          <Route index element={<ChatDashboard />} />
          <Route path="run/:runId" element={<RunViewer />} />
        </Route>
      </Routes>
    </Router>
  );
}
