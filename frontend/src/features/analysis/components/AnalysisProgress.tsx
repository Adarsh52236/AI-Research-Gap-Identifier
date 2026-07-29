import { useState, useEffect } from 'react';
import { PROGRESS_MESSAGES } from '../constants/progressMessages';

export function AnalysisProgress() {
  const [messageIndex, setMessageIndex] = useState(0);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  useEffect(() => {
    const msgInterval = setInterval(() => {
      setMessageIndex((prev) => (prev + 1) % PROGRESS_MESSAGES.length);
    }, 4000);

    const timeInterval = setInterval(() => {
      setElapsedSeconds((prev) => prev + 1);
    }, 1000);

    return () => {
      clearInterval(msgInterval);
      clearInterval(timeInterval);
    };
  }, []);

  return (
    <div className="bg-surface rounded-xl shadow-sm border border-border p-12 flex flex-col items-center justify-center min-h-[300px]">
      <h3 className="text-xl font-bold text-text mb-6">Analyzing AI Literature</h3>
      
      <div className="w-full max-w-md bg-gray-100 rounded-full h-2 mb-8 overflow-hidden relative">
        <div className="absolute top-0 bottom-0 left-0 bg-primary w-1/3 rounded-full animate-[progress_2s_ease-in-out_infinite]"></div>
      </div>
      
      <p className="text-primary font-medium text-lg text-center animate-pulse transition-opacity duration-500 mb-2">
        {PROGRESS_MESSAGES[messageIndex]}
      </p>

      <div className="text-sm font-mono text-muted mb-8">
        Elapsed: {Math.floor(elapsedSeconds / 60)}:{(elapsedSeconds % 60).toString().padStart(2, '0')}
      </div>
      
      <p className="text-xs text-gray-400 max-w-md text-center">
        This process involves retrieving scholarly papers, clustering embeddings via BERTopic, and utilizing LLMs to synthesize research gaps.
      </p>

      <style>{`
        @keyframes progress {
          0% { left: -33%; }
          100% { left: 100%; }
        }
      `}</style>
    </div>
  );
}
