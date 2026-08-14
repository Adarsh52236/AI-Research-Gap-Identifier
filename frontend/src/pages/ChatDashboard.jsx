import React, { useEffect, useState, useRef } from 'react';
import ChatThread from '../components/chat/ChatThread';
import ChatComposer from '../components/chat/ChatComposer';
import { runsService } from '../services/runsService';
import useAppStore from '../store/useAppStore';

export default function ChatDashboard() {
  const { 
    activeRunId, setActiveRunId, 
    messagesByRunId, addMessage, updateMessage,
    addRun, updateRun
  } = useAppStore();
  
  const [isRunning, setIsRunning] = useState(false);
  const [loadingText, setLoadingText] = useState('');
  const pollIntervalRef = useRef(null);

  // If there's an active run, we show its messages, otherwise empty.
  const messages = activeRunId ? (messagesByRunId[activeRunId] || []) : [];

  const handleSend = async (payload) => {
    try {
      setIsRunning(true);
      setLoadingText('Starting analysis...');
      
      // Temporary local run ID until backend responds
      const tempId = `local_${Date.now()}`;
      setActiveRunId(tempId);
      
      addMessage(tempId, {
        id: Date.now().toString(),
        role: 'user',
        content: payload.query,
        createdAt: new Date().toISOString()
      });

      const res = await runsService.startPipelineRun(payload);
      const newRunId = res.run_id;
      
      // Swap tempId with newRunId in state
      useAppStore.setState(state => {
        const msgs = state.messagesByRunId[tempId] || [];
        const newMessagesByRunId = { ...state.messagesByRunId, [newRunId]: msgs };
        delete newMessagesByRunId[tempId];
        return { 
          activeRunId: newRunId, 
          messagesByRunId: newMessagesByRunId 
        };
      });

      addRun({
        run_id: newRunId,
        query: payload.query,
        status: res.status,
        started_at: new Date().toISOString()
      });

      startPolling(newRunId);

    } catch (error) {
      console.error(error);
      setIsRunning(false);
      // add error message
      if (activeRunId) {
        addMessage(activeRunId, {
          id: Date.now().toString(),
          role: 'assistant',
          content: 'An error occurred while starting the analysis.',
          createdAt: new Date().toISOString()
        });
      }
    }
  };

  const startPolling = (runId) => {
    if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    
    pollIntervalRef.current = setInterval(async () => {
      try {
        const statusRes = await runsService.getRunStatus(runId);
        updateRun(runId, statusRes);
        
        if (statusRes.current_step) {
           setLoadingText(`Running step: ${statusRes.current_step}...`);
        }

        if (statusRes.status === 'completed' || statusRes.status === 'failed') {
          clearInterval(pollIntervalRef.current);
          setIsRunning(false);
          
          if (statusRes.status === 'completed') {
             setLoadingText('Fetching report...');
             try {
               const reportRes = await runsService.getRunReport(runId);
               addMessage(runId, {
                 id: Date.now().toString(),
                 role: 'assistant',
                 content: reportRes.content,
                 createdAt: new Date().toISOString()
               });
             } catch (err) {
               addMessage(runId, {
                 id: Date.now().toString(),
                 role: 'assistant',
                 content: 'Analysis completed, but report could not be fetched.',
                 createdAt: new Date().toISOString()
               });
             }
          } else {
             addMessage(runId, {
               id: Date.now().toString(),
               role: 'assistant',
               content: `Analysis failed. Errors:\n\n${statusRes.errors_json || 'Unknown error'}`,
               createdAt: new Date().toISOString()
             });
          }
        }
      } catch (err) {
        console.error("Poll error", err);
      }
    }, 3000);
  };

  useEffect(() => {
    return () => {
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    };
  }, []);

  return (
    <div className="flex flex-col h-full relative">
      {messages.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center text-center px-4 animate-in fade-in duration-500">
          <div className="w-16 h-16 bg-panel shadow-sm border border-border rounded-2xl flex items-center justify-center mb-6 text-accent">
            <span className="font-serif text-2xl font-bold">G</span>
          </div>
          <h2 className="text-2xl font-serif text-text mb-2">How can I help you research today?</h2>
          <p className="text-muted font-sans text-sm max-w-md">
            Ask a complex question to kick off an automated pipeline that searches, downloads, extracts, and synthesizes recent academic literature.
          </p>
        </div>
      ) : (
        <ChatThread messages={messages} isRunning={isRunning} loadingText={loadingText} />
      )}
      
      <div className="shrink-0 pt-2 pb-6 w-full max-w-3xl mx-auto bg-bg z-10 sticky bottom-0">
        <ChatComposer onSend={handleSend} isRunning={isRunning} />
      </div>
    </div>
  );
}
