import { useEffect, useRef } from 'react';
import { useChatStore } from '@/features/chat/store/chatStore';
import { ChatInput } from './ChatInput';
import { ResearchProgress } from './ResearchProgress';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Bot, User, AlertCircle } from 'lucide-react';
import { useParams } from 'react-router-dom';

export function ChatInterface() {
  const { id } = useParams();
  const { messages, isLoading, isSending, isResearching, error, fetchMessages, sendMessage, setCurrentSession } = useChatStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (id) {
      fetchMessages(id);
    } else {
      setCurrentSession(null);
    }
  }, [id, fetchMessages, setCurrentSession]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = (content: string) => {
    sendMessage(content, id);
  };

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center px-4 max-w-2xl mx-auto">
            <h1 className="text-3xl font-bold text-text mb-2">ResearchOS</h1>
            <h2 className="text-xl text-gray-500 mb-8">What would you like to research today?</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full mt-8">
              {[
                "Find Research Gaps",
                "Literature Review",
                "Compare Papers",
                "Upload Research Paper",
                "Analyze Existing Draft"
              ].map((suggestion, i) => (
                <button
                  key={i}
                  onClick={() => handleSendMessage(suggestion)}
                  className="flex items-center text-left p-4 rounded-xl border border-gray-200 hover:border-primary/50 hover:bg-gray-50 transition-colors text-sm text-gray-600 font-medium"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="max-w-3xl mx-auto w-full py-8 px-4 space-y-6">
            {messages.map((msg, idx) => {
              if (msg.role === 'tool') {
                return null; // We will handle tool calls via ResearchProgress component if needed, or hide raw outputs
              }

              const isUser = msg.role === 'user';
              
              // Skip empty assistant messages that were just tool calls
              if (!isUser && !msg.content) return null;

              return (
                <div key={idx} className={`flex gap-4 ${isUser ? 'flex-row-reverse' : ''}`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 mt-1 ${
                    isUser ? 'bg-primary/10 text-primary' : 'bg-primary text-white shadow-sm'
                  }`}>
                    {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                  </div>
                  <div className={`flex-1 overflow-hidden ${isUser ? 'flex justify-end' : ''}`}>
                    <div className={`prose max-w-none text-text ${
                      isUser 
                        ? 'bg-gray-50 border border-gray-200 px-5 py-4 rounded-2xl rounded-tr-sm inline-block text-left text-gray-800' 
                        : 'bg-white border border-border px-6 py-5 rounded-2xl rounded-tl-sm shadow-sm hover:shadow-md transition-shadow duration-200'
                    }`}>
                      {isUser ? (
                        <div className="whitespace-pre-wrap font-medium">{msg.content}</div>
                      ) : (
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {msg.content}
                        </ReactMarkdown>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
            
            {isLoading && (
               <div className="flex justify-center py-4">
                 <div className="animate-pulse text-muted text-sm">Loading history...</div>
               </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="relative z-10">
        <ResearchProgress isResearching={isResearching} />
        {error && (
          <div className="max-w-3xl mx-auto px-4 mb-2">
            <div className="flex items-center gap-2 text-sm text-red-600 bg-red-50 border border-red-200 rounded-xl px-4 py-3">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          </div>
        )}
        <ChatInput onSendMessage={handleSendMessage} isSending={isSending} />
      </div>
    </div>
  );
}
