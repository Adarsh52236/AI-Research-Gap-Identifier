import React, { useState } from 'react';
import useAppStore from '../../store/useAppStore';
import { DEBUG } from '../../config/debug';

export default function DebugPanel() {
  const [isExpanded, setIsExpanded] = useState(false);
  const debugState = useAppStore(state => state.debugState);

  if (!DEBUG) return null;

  const toggle = () => setIsExpanded(!isExpanded);

  return (
    <div className="fixed bottom-0 left-0 z-50 w-full font-mono text-xs">
      <div 
        className="bg-gray-800 text-gray-200 px-4 py-1 flex justify-between items-center cursor-pointer hover:bg-gray-700 border-t border-gray-600"
        onClick={toggle}
      >
        <div className="flex space-x-4">
          <span className="font-bold text-yellow-400">DEBUG MODE</span>
          <span>{debugState.lastError ? <span className="text-red-400">Error!</span> : 'All Systems Nominal'}</span>
        </div>
        <div>
          {isExpanded ? '▼ Hide Details' : '▲ Show Details'}
        </div>
      </div>
      
      {isExpanded && (
        <div className="bg-gray-900 text-green-400 p-4 max-h-64 overflow-y-auto space-y-3 opacity-95">
          <div>
            <strong className="text-gray-400 block mb-1">Environment Config:</strong>
            VITE_API_BASE_URL: {import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'}
          </div>
          
          <div>
            <strong className="text-gray-400 block mb-1">Last API Request:</strong>
            {debugState.lastRequest ? (
              <pre className="whitespace-pre-wrap text-[10px]">
                {debugState.lastRequest.method} {debugState.lastRequest.url}
                <br/>
                Status: {debugState.lastRequest.status}
                <br/>
                Backend Request ID: {debugState.lastRequest.request_id || 'None'}
              </pre>
            ) : 'None'}
          </div>

          <div>
            <strong className="text-gray-400 block mb-1">Last Poll Status:</strong>
            {debugState.lastPollStatus ? (
              <pre className="whitespace-pre-wrap text-[10px]">
                Run ID: {debugState.lastPollStatus.run_id}
                <br/>
                Status: {debugState.lastPollStatus.status}
                <br/>
                Current Step: {debugState.lastPollStatus.current_step || 'N/A'}
              </pre>
            ) : 'None'}
          </div>

          <div>
            <strong className="text-gray-400 block mb-1">Last Error:</strong>
            {debugState.lastError ? (
              <pre className="whitespace-pre-wrap text-red-400 text-[10px]">
                {debugState.lastError}
              </pre>
            ) : 'None'}
          </div>
        </div>
      )}
    </div>
  );
}
