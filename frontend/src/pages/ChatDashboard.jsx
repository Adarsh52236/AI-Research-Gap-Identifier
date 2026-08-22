import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import ChatThread from '../components/chat/ChatThread';
import ChatComposer from '../components/chat/ChatComposer';
import { runsService } from '../services/runsService';
import { chatService } from '../services/chatService';
import useAppStore from '../store/useAppStore';
import useChatStore from '../store/useChatStore';
import { DEBUG } from '../config/debug';
import DebugPanel from '../components/common/DebugPanel';

export default function ChatDashboard() {
  const { sessionId: urlSessionId } = useParams();
  const navigate = useNavigate();

  const { addRun, updateRun, runs } = useAppStore();
  const { 
    sessions, activeSessionId, setActiveSessionId, 
    messagesBySessionId, fetchMessages, createSession,
    addLocalMessage, updateLocalMessage
  } = useChatStore();
  
  const [isRunning, setIsRunning] = useState(false);
  const [loadingText, setLoadingText] = useState('');
  const pollIntervalRef = useRef(null);

  // Sync URL with state
  useEffect(() => {
    if (urlSessionId) {
      setActiveSessionId(urlSessionId);
      if (!messagesBySessionId[urlSessionId]) {
        fetchMessages(urlSessionId);
      }
    } else {
      setActiveSessionId(null);
    }
  }, [urlSessionId, setActiveSessionId, fetchMessages, messagesBySessionId]);

  // Handle Polling Persistence (Issue 2)
  useEffect(() => {
    if (urlSessionId && !isRunning) {
      // Check if there is an active run for this session
      const activeRun = runs.find(r => r.session_id === urlSessionId && ['pending', 'running'].includes(r.status));
      if (activeRun) {
        setIsRunning(true);
        setLoadingText('Resuming analysis tracking...');
        
        // Ensure there is a pending message in the UI to attach the loader to
        const msgs = messagesBySessionId[urlSessionId] || [];
        const existingPending = msgs.find(m => m.isPending);
        const pendingMsgId = existingPending ? existingPending.id : `pending_${Date.now()}`;
        
        if (!existingPending) {
           addLocalMessage(urlSessionId, {
             id: pendingMsgId,
             role: 'assistant',
             content: '',
             run_id: activeRun.run_id,
             created_at: new Date().toISOString(),
             isPending: true
           });
        }
        
        startPolling(activeRun.run_id, urlSessionId, pendingMsgId);
      }
    }
  }, [urlSessionId, runs]); // Only run when URL or global runs change

  const baseMessages = activeSessionId ? (messagesBySessionId[activeSessionId] || []) : [];
  
  const displayMessages = [
    {
      id: 'greeting',
      role: 'assistant',
      content: 'Hello! I am GapFinder AI. How can I help you research today? You can ask me to analyze literature on any complex topic to identify research gaps.',
      created_at: new Date(0).toISOString()
    },
    ...baseMessages
  ];

  const handleSend = async (payload) => {
    try {
      setIsRunning(true);
      setLoadingText('Thinking...');
      
      let currentSessionId = activeSessionId;
      
      // 1. Create session if none exists
      if (!currentSessionId) {
        const title = payload.query.slice(0, 40) + (payload.query.length > 40 ? "..." : "");
        const newSession = await createSession(title);
        currentSessionId = newSession.id;
        navigate(`/app/chat/${currentSessionId}`, { replace: true });
      }

      // Add local user message immediately for UI responsiveness
      const tempUserMsgId = `temp_${Date.now()}`;
      addLocalMessage(currentSessionId, {
        id: tempUserMsgId,
        role: 'user',
        content: payload.query,
        created_at: new Date().toISOString()
      });

      // 2. Call Mediator endpoint
      const response = await chatService.orchestrateChat(currentSessionId, payload);

      // We can replace the temp user message with the real one later, but for now we just rely on next fetch.

      if (response.type === "chat") {
         // It's a casual chat response
         addLocalMessage(currentSessionId, response.message);
         setIsRunning(false);
      } else if (response.type === "analysis") {
         // It's a research analysis task
         const newRunId = response.run_id;
         setLoadingText('Starting analysis...');
         
         const pendingMsgId = `pending_${Date.now()}`;
         addLocalMessage(currentSessionId, {
           id: pendingMsgId,
           role: 'assistant',
           content: '',
           run_id: newRunId,
           created_at: new Date().toISOString(),
           isPending: true
         });

         addRun({
           run_id: newRunId,
           query: response.topic,
           status: 'pending',
           started_at: new Date().toISOString(),
           session_id: currentSessionId
         });

         startPolling(newRunId, currentSessionId, pendingMsgId);
      }

    } catch (error) {
      console.error(error);
      setIsRunning(false);
      
      if (activeSessionId) {
        addLocalMessage(activeSessionId, {
          id: Date.now().toString(),
          role: 'assistant',
          content: 'An error occurred while processing your message.',
          created_at: new Date().toISOString()
        });
      }
    }
  };

  const handleStop = () => {
    if (pollIntervalRef.current) clearTimeout(pollIntervalRef.current);
    setIsRunning(false);
    if (activeSessionId) {
      addLocalMessage(activeSessionId, {
        id: Date.now().toString(),
        role: 'assistant',
        content: 'Execution terminated by user.',
        created_at: new Date().toISOString()
      });
    }
  };

  function startPolling(runId, sessionId, pendingMsgId) {
    if (pollIntervalRef.current) clearTimeout(pollIntervalRef.current);
    
    let pollInterval = 2000;
    const maxInterval = 10000;
    
    const poll = async () => {
      try {
        const statusRes = await runsService.getRunStatus(runId);
        updateRun(runId, statusRes);
        useAppStore.getState().setDebugState({
          lastPollStatus: { run_id: runId, status: statusRes.status, current_step: statusRes.current_step }
        });
        
        if (statusRes.current_step) {
           setLoadingText(`Running step: ${statusRes.current_step}...`);
        }

        if (statusRes.status === 'completed' || statusRes.status === 'failed') {
          setIsRunning(false);
          
          if (statusRes.status === 'completed') {
             setLoadingText('Fetching report...');
             try {
               const reportRes = await runsService.getRunReport(runId);
               
               // Save final message to backend
               const savedMsg = await chatService.createMessage(sessionId, 'assistant', reportRes.content, runId);
               
               // Replace local pending message with saved msg
               useChatStore.getState().updateLocalMessage(sessionId, pendingMsgId, {
                  ...savedMsg,
                  isPending: false
               });

             } catch (err) {
               updateLocalMessage(sessionId, pendingMsgId, {
                 content: 'Analysis completed, but report could not be fetched.',
                 isPending: false
               });
             }
          } else {
             updateLocalMessage(sessionId, pendingMsgId, {
               content: `Analysis failed. Errors:\n\n${JSON.stringify(statusRes.errors) || 'Unknown error'}`,
               isPending: false
             });
          }
          return; // Stop polling
        }
        
        pollInterval = Math.min(pollInterval * 1.5, maxInterval);
        pollIntervalRef.current = setTimeout(poll, pollInterval);
        
      } catch (err) {
        pollInterval = Math.min(pollInterval * 1.5, maxInterval);
        pollIntervalRef.current = setTimeout(poll, pollInterval);
      }
    };
    
    pollIntervalRef.current = setTimeout(poll, pollInterval);
  };

  useEffect(() => {
    return () => {
      if (pollIntervalRef.current) {
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
