import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { runsService } from '../services/runsService';
import MarkdownMessage from '../components/chat/MarkdownMessage';
import useAppStore from '../store/useAppStore';
import { MessageSquare, ArrowLeft, Loader2 } from 'lucide-react';

export default function RunViewer() {
  const { runId } = useParams();
  const navigate = useNavigate();
  const { setActiveRunId } = useAppStore();
  const [reportContent, setReportContent] = useState('');
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadRun() {
      try {
        setLoading(true);
        const st = await runsService.getRunStatus(runId);
        setStatus(st);
        if (st.status === 'completed' && st.report_path) {
          const rep = await runsService.getRunReport(runId);
          setReportContent(rep.content);
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    loadRun();
  }, [runId]);

  const handleOpenInChat = () => {
    setActiveRunId(runId);
    navigate('/app');
  };

  if (loading) {
    return <div className="flex-1 flex items-center justify-center text-muted"><Loader2 className="animate-spin" /></div>;
  }

  if (!status) {
    return <div className="flex-1 flex items-center justify-center text-muted">Run not found.</div>;
  }

  return (
    <div className="flex-1 flex flex-col h-full py-6">
      <div className="flex items-center justify-between mb-8 border-b border-border pb-4">
        <div>
          <button onClick={() => navigate(-1)} className="flex items-center gap-1 text-muted hover:text-text mb-2 text-sm transition-colors">
            <ArrowLeft size={16} /> Back
          </button>
          <h1 className="text-xl font-serif text-text">Run: {status.query || runId}</h1>
          <div className="text-sm text-muted mt-1 flex gap-4">
            <span>Status: {status.status}</span>
            <span>Papers: {status.papers_found}</span>
          </div>
        </div>
        <button 
          onClick={handleOpenInChat}
          className="flex items-center gap-2 bg-panel border border-border text-text px-4 py-2 rounded-lg hover:bg-border transition-colors text-sm"
        >
          <MessageSquare size={16} />
          Open in Chat
        </button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {reportContent ? (
          <div className="bg-panel rounded-2xl p-6 shadow-sm border border-border">
            <MarkdownMessage content={reportContent} />
          </div>
        ) : (
          <div className="text-muted text-center py-10">No report available for this run.</div>
        )}
      </div>
    </div>
  );
}
