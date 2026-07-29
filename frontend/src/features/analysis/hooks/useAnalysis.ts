import { useState, useRef, useCallback } from 'react';
import { analysisApi } from '@/api/analysis';
import { AnalysisError } from '../types';
import { useAnalysisStore } from '@/store/analysisStore';

export type AnalysisStatus = 'idle' | 'loading' | 'success' | 'error';

export function useAnalysis() {
  const [status, setStatus] = useState<AnalysisStatus>('idle');
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  
  const { sessions, addSession } = useAnalysisStore();
  const currentSession = sessions.find(s => s.id === currentSessionId);
  
  const abortControllerRef = useRef<AbortController | null>(null);

  const runAnalysis = useCallback(async (query: string, maxResults: number) => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    const controller = new AbortController();
    abortControllerRef.current = controller;

    const newId = crypto.randomUUID();
    setCurrentSessionId(newId);
    setStatus('loading');

    try {
      const response = await analysisApi.runAnalysis(query, maxResults, controller.signal);
      
      addSession({
        id: newId,
        timestamp: new Date().toISOString(),
        query,
        status: 'success',
        data: response,
        metadata: {
          paperCount: response.papers_indexed,
          topicCount: response.topics.topics.length,
          gapCount: response.gaps.total_gaps,
          durationSeconds: response.duration_seconds
        }
      });
      
      setStatus('success');
    } catch (err: any) {
      if (err.message === 'Request cancelled') {
        return;
      }
      
      let errorType: AnalysisError['type'] = 'unknown';
      let message = err.message || 'An unexpected error occurred.';
      
      if (message.includes('Failed to fetch') || message.includes('NetworkError')) {
        errorType = 'network';
        message = 'Unable to connect to the ResearchOS backend. Please ensure the server is running.';
      } else if (message.includes('422') || message.includes('Validation')) {
        errorType = 'validation';
      } else if (message.includes('500') || message.includes('Internal')) {
        errorType = 'server';
      }
      
      addSession({
        id: newId,
        timestamp: new Date().toISOString(),
        query,
        status: 'error',
        error: {
          type: errorType,
          message,
          retryable: errorType === 'network' || errorType === 'server'
        }
      });
      
      setStatus('error');
    } finally {
      if (abortControllerRef.current === controller) {
        abortControllerRef.current = null;
      }
    }
  }, [addSession]);

  const loadSession = useCallback((id: string) => {
    const session = sessions.find(s => s.id === id);
    if (session) {
      setCurrentSessionId(session.id);
      setStatus(session.status);
    }
  }, [sessions]);

  const reset = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setCurrentSessionId(null);
    setStatus('idle');
  }, []);

  return {
    status,
    data: currentSession?.data || null,
    error: currentSession?.error || null,
    currentSessionId,
    runAnalysis,
    loadSession,
    reset,
  };
}
