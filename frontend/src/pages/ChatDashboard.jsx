import React, { useEffect, useState, useRef } from 'react';
import ChatThread from '../components/chat/ChatThread';
import ChatComposer from '../components/chat/ChatComposer';
import { runsService } from '../services/runsService';
import useAppStore from '../store/useAppStore';
import { DEBUG } from '../config/debug';
import DebugPanel from '../components/common/DebugPanel';

export default function ChatDashboard() {
  const { 
    activeRunId, setActiveRunId, 
    messagesByRunId, addMessage, updateMessage,
    addRun, updateRun, runs
  } = useAppStore();
  
  const [isRunning, setIsRunning] = useState(false);
  const [loadingText, setLoadingText] = useState('');
  const pollIntervalRef = useRef(null);
  const [sessionRunIds, setSessionRunIds] = useState([]);

  useEffect(() => {
    if (!activeRunId) {
      setSessionRunIds([]);
    } else {
      const activeRun = runs.find(r => r.run_id === activeRunId);
      if (activeRun) {
        const sId = activeRun.session_id || activeRun.run_id;
        const sessionRuns = runs
          .filter(r => (r.session_id || r.run_id) === sId)
          .sort((a, b) => new Date(a.started_at) - new Date(b.started_at))
          .map(r => r.run_id);
          
        setSessionRunIds(prev => {
          // Keep tempIds if they exist
          const tempIds = prev.filter(id => id.startsWith('local_'));
          const newSessionRunIds = [...sessionRuns, ...tempIds];
          // Only update if arrays are different to avoid infinite loops
          if (JSON.stringify(prev) !== JSON.stringify(newSessionRunIds)) {
            return newSessionRunIds;
          }
          return prev;
        });
      } else {
        setSessionRunIds(prev => prev.includes(activeRunId) ? prev : [activeRunId]);
      }
    }
  }, [activeRunId, runs]);

  const baseMessages = sessionRunIds.flatMap(id => messagesByRunId[id] || []);
  
  const displayMessages = [
    {
      id: 'greeting',
      role: 'assistant',
      content: 'Hello! I am GapFinder AI. How can I help you research today? You can ask me to analyze literature on any complex topic to identify research gaps.',
      createdAt: new Date(0).toISOString()
    },
    ...baseMessages
  ];

  const handleSend = async (payload) => {
    try {
      setIsRunning(true);
      setLoadingText('Starting analysis...');
      
      // Temporary local run ID until backend responds
      const tempId = `local_${Date.now()}`;
      setSessionRunIds(prev => [...prev, tempId]);
      setActiveRunId(tempId);
      
      addMessage(tempId, {
        id: Date.now().toString(),
        role: 'user',
        content: payload.query,
        createdAt: new Date().toISOString()
      });

      // Find the first valid run ID to use as the session_id
      const validSessionId = sessionRunIds.find(id => !id.startsWith('local_'));
      
      const res = await runsService.startPipelineRun({
        ...payload,
        session_id: validSessionId || undefined
      });
      const newRunId = res.run_id;
      
      if (!newRunId) {
        throw new Error("Failed to start analysis: No run ID received.");
      }
      
      setSessionRunIds(prev => prev.map(id => id === tempId ? newRunId : id));
      
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

  const handleStop = () => {
    if (pollIntervalRef.current) clearTimeout(pollIntervalRef.current);
    setIsRunning(false);
    if (activeRunId) {
      addMessage(activeRunId, {
        id: Date.now().toString(),
        role: 'assistant',
        content: 'Execution terminated by user.',
        createdAt: new Date().toISOString()
      });
    }
  };

  const startPolling = (runId) => {
    if (pollIntervalRef.current) clearTimeout(pollIntervalRef.current);
    
    const pollSessionId = crypto.randomUUID();
    let pollInterval = 2000;
    const maxInterval = 10000;
    let notFoundCount = 0;
    let networkErrorCount = 0;
    let consecutive502s = 0;
    
    if (DEBUG) console.log(`[POLL START] run_id=${runId}, pollSessionId=${pollSessionId}`);
    
    const poll = async () => {
      try {
        if (DEBUG) console.log(`[POLL TICK] run_id=${runId}, pollSessionId=${pollSessionId}`);
        const statusRes = await runsService.getRunStatus(runId);
        // Reset counters on success
        notFoundCount = 0;
        networkErrorCount = 0;
        consecutive502s = 0;
        
        updateRun(runId, statusRes);
        useAppStore.getState().setDebugState({
          lastPollStatus: { run_id: runId, status: statusRes.status, current_step: statusRes.current_step }
        });
        
        if (statusRes.current_step) {
           setLoadingText(`Running step: ${statusRes.current_step}...`);
        }

        if (statusRes.status === 'completed' || statusRes.status === 'failed') {
          setIsRunning(false);
          
          if (DEBUG) console.log(`[POLL STOP] reason=${statusRes.status}`);
          
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
               content: `Analysis failed. Errors:\n\n${JSON.stringify(statusRes.errors) || 'Unknown error'}`,
               createdAt: new Date().toISOString()
             });
          }
          return; // Stop polling
        }
        
        // Increase backoff slightly for next poll, up to maxInterval
        pollInterval = Math.min(pollInterval * 1.5, maxInterval);
        pollIntervalRef.current = setTimeout(poll, pollInterval);
        
      } catch (err) {
        if (DEBUG) console.error(`[POLL ERROR TICK] run_id=${runId}, pollSessionId=${pollSessionId}`, err);
        
        if (err.response && err.response.status === 404) {
          notFoundCount++;
          if (notFoundCount >= 2) {
            setIsRunning(false);
            if (DEBUG) console.log(`[POLL STOP] reason=404_limit`);
            addMessage(runId, {
              id: Date.now().toString(),
              role: 'assistant',
              content: 'Run not found. Please restart analysis.',
              createdAt: new Date().toISOString()
            });
            return;
          }
        } else if (err.response && [502, 503, 504].includes(err.response.status)) {
          consecutive502s++;
          if (consecutive502s >= 5) {
            setIsRunning(false);
            if (DEBUG) console.log(`[POLL STOP] reason=502_limit`);
            addMessage(runId, {
              id: Date.now().toString(),
              role: 'assistant',
              content: 'Backend is unresponsive. Please try again later.',
              createdAt: new Date().toISOString()
            });
            return;
          }
          setLoadingText("Temporary backend issue; retrying...");
          pollInterval = Math.min(pollInterval * 2, 15000); // Slow down significantly
        } else {
          networkErrorCount++;
          if (networkErrorCount >= 5) {
            setIsRunning(false);
            if (DEBUG) console.log(`[POLL STOP] reason=network_error_limit`);
            addMessage(runId, {
              id: Date.now().toString(),
              role: 'assistant',
              content: 'Backend may be sleeping. Try again.',
              createdAt: new Date().toISOString()
            });
            return;
          }
        }
        // Retry with backoff
        pollInterval = Math.min(pollInterval * 1.5, maxInterval);
        pollIntervalRef.current = setTimeout(poll, pollInterval);
      }
    };
    
    pollIntervalRef.current = setTimeout(poll, pollInterval);
  };

  useEffect(() => {
    return () => {
      if (pollIntervalRef.current) {
        if (DEBUG) console.log(`[POLL STOP] reason=unmounted`);
        clearTimeout(pollIntervalRef.current);
      }
    };
  }, []);

  return (
    <div className="flex flex-col h-full relative">
      <ChatThread messages={displayMessages} isRunning={isRunning} loadingText={loadingText} />
      
      <div className="shrink-0 pt-2 pb-6 w-full max-w-3xl mx-auto bg-bg z-10 sticky bottom-0">
        <ChatComposer onSend={handleSend} onStop={handleStop} isRunning={isRunning} />
      </div>
      <DebugPanel />
    </div>
  );
}
