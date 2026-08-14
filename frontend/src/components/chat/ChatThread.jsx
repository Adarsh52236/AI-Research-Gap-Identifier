import React, { useEffect, useRef } from 'react';
import MarkdownMessage from './MarkdownMessage';
import clsx from 'clsx';
import { User } from 'lucide-react';

export default function ChatThread({ messages, isRunning, loadingText }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isRunning, loadingText]);

  return (
    <div className="flex-1 overflow-y-auto w-full py-8 space-y-8 scroll-smooth">
      {messages.map((msg) => (
        <div key={msg.id} className={clsx("flex w-full", msg.role === 'user' ? "justify-end" : "justify-start")}>
          {msg.role === 'user' ? (
            <div className="bg-accentSoft text-text px-5 py-3.5 rounded-2xl max-w-[85%] text-base shadow-sm border border-accent/10">
              <div className="mt-0.5">
                {msg.content}
              </div>
            </div>
          ) : (
            <div className="w-full text-text py-2">
              <MarkdownMessage content={msg.content} />
            </div>
          )}
        </div>
      ))}
      {isRunning && (
        <div className="flex w-full justify-start animate-pulse">
          <div className="w-full text-text py-2 text-muted italic flex items-center gap-2">
            <div className="w-4 h-4 border-2 border-accent border-t-transparent rounded-full animate-spin shrink-0"></div>
            {loadingText || "Analyzing..."}
          </div>
        </div>
      )}
      <div ref={bottomRef} className="h-4" />
    </div>
  );
}
