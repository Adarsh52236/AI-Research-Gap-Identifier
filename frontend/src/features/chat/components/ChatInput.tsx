import { useState, useRef, useEffect } from 'react';
import { Send, Paperclip, Search, Loader2 } from 'lucide-react';

interface ChatInputProps {
  onSendMessage: (content: string) => void;
  isSending: boolean;
}

export function ChatInput({ onSendMessage, isSending }: ChatInputProps) {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [input]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isSending) return;
    
    onSendMessage(input);
    setInput('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="bg-transparent p-4 pb-6">
      <div className="max-w-3xl mx-auto relative">
        <form 
          onSubmit={handleSubmit}
          className="relative flex items-end bg-surface border border-border rounded-2xl shadow-[0_4px_20px_rgba(0,0,0,0.04)] focus-within:ring-1 focus-within:ring-primary focus-within:border-primary overflow-hidden transition-all"
        >
          {/* Action Buttons (Left) */}
          <div className="flex px-3 pb-3">
            <button
              type="button"
              className="p-1.5 text-muted hover:text-text rounded-md hover:bg-gray-100 transition-colors"
              title="Upload PDF (Coming Soon)"
            >
              <Paperclip className="w-5 h-5" />
            </button>
            <button
              type="button"
              className="p-1.5 text-muted hover:text-text rounded-md hover:bg-gray-100 transition-colors ml-1"
              title="Web Search (Coming Soon)"
            >
              <Search className="w-5 h-5" />
            </button>
          </div>

          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question or request research on a topic..."
            className="flex-1 max-h-[200px] py-4 px-2 bg-transparent border-none resize-none focus:ring-0 text-text outline-none placeholder:text-muted"
            rows={1}
            disabled={isSending}
          />

          <div className="px-3 pb-3">
            <button
              type="submit"
              disabled={!input.trim() || isSending}
              className={`p-2 rounded-xl flex items-center justify-center transition-colors ${
                !input.trim() || isSending
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : 'bg-primary text-white hover:bg-blue-600 shadow-sm'
              }`}
            >
              {isSending ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Send className="w-5 h-5" />
              )}
            </button>
          </div>
        </form>
        <div className="text-center mt-3 text-xs text-muted">
          ResearchOS can make mistakes. Consider verifying important information before citing.
        </div>
      </div>
    </div>
  );
}
