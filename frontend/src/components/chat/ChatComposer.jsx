import React, { useState, useRef } from 'react';
import { Send, Settings2, Loader2, Paperclip, X } from 'lucide-react';
import clsx from 'clsx';
import api from '../../services/api';

export default function ChatComposer({ onSend, isRunning }) {
  const [query, setQuery] = useState('');
  const [showSettings, setShowSettings] = useState(false);
  const [limit, setLimit] = useState(5);
  const [sources, setSources] = useState(['arxiv', 'semantic_scholar']);
  
  const fileInputRef = useRef(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedFileName, setUploadedFileName] = useState('');
  const [uploadedFileText, setUploadedFileText] = useState('');

  const handleSend = () => {
    if (!query.trim() || isRunning) return;
    onSend({
      query: query.trim(),
      limit,
      sources,
      user_document_text: uploadedFileText || null,
      steps: ["search", "download", "extract", "mine", "index", "report"]
    });
    setQuery('');
    setUploadedFileName('');
    setUploadedFileText('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const toggleSource = (src) => {
    setSources(prev => prev.includes(src) ? prev.filter(s => s !== src) : [...prev, src]);
  };
  
  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await api.post("/analysis/upload-user-document/", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      setUploadedFileName(res.data.filename);
      setUploadedFileText(res.data.extracted_text);
    } catch (err) {
      console.error("Upload failed", err);
      alert("Failed to extract text from document.");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <div className="bg-panel rounded-2xl shadow-[var(--shadow)] border border-border p-4 w-full flex flex-col gap-3 relative transition-all duration-300">
      {showSettings && (
        <div className="flex flex-wrap gap-4 px-2 py-2 border-b border-border text-sm mb-1 animate-in slide-in-from-bottom-2">
          <div className="flex items-center gap-2">
            <span className="text-muted font-medium">Sources:</span>
            <label className="flex items-center gap-1 cursor-pointer">
              <input type="checkbox" checked={sources.includes('arxiv')} onChange={() => toggleSource('arxiv')} className="accent-accent" />
              <span>ArXiv</span>
            </label>
            <label className="flex items-center gap-1 cursor-pointer">
              <input type="checkbox" checked={sources.includes('semantic_scholar')} onChange={() => toggleSource('semantic_scholar')} className="accent-accent" />
              <span>Semantic Scholar</span>
            </label>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-muted font-medium">Papers limit:</span>
            <input 
              type="number" 
              min="1" max="20" 
              value={limit} 
              onChange={e => setLimit(Number(e.target.value))}
              className="w-16 bg-bg border border-border rounded-md px-2 py-1 outline-none focus:border-accent"
            />
          </div>
        </div>
      )}
      
      {uploadedFileName && (
        <div className="flex items-center gap-2 px-2 py-1 mb-1 text-sm text-accent bg-accentSoft rounded-md w-fit">
          <Paperclip size={14} />
          <span className="truncate max-w-[200px]">{uploadedFileName}</span>
          <button onClick={() => { setUploadedFileName(''); setUploadedFileText(''); }} className="hover:text-red-500 ml-1">
            <X size={14} />
          </button>
        </div>
      )}
      
      <div className="flex items-end gap-2">
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a research question..."
          className="flex-1 bg-transparent resize-none max-h-32 min-h-[44px] outline-none placeholder:text-muted/60 py-2.5 px-2"
          rows={1}
          disabled={isRunning || isUploading}
        />
        
        <input 
          type="file" 
          ref={fileInputRef} 
          style={{ display: 'none' }} 
          accept=".pdf,.txt,.md" 
          onChange={handleFileUpload} 
        />
        
        <div className="flex items-center gap-2 pb-1 shrink-0">
          <button 
            onClick={() => fileInputRef.current?.click()}
            className="p-2 rounded-xl transition-colors text-muted hover:bg-border hover:text-text"
            title="Upload Research Document"
            disabled={isRunning || isUploading}
          >
            {isUploading ? <Loader2 size={20} className="animate-spin" /> : <Paperclip size={20} />}
          </button>
          
          <button 
            onClick={() => setShowSettings(!showSettings)}
            className={clsx("p-2 rounded-xl transition-colors", showSettings ? "bg-accentSoft text-accent" : "text-muted hover:bg-border hover:text-text")}
            title="Analysis Settings"
            disabled={isRunning || isUploading}
          >
            <Settings2 size={20} />
          </button>
          
          <button
            onClick={handleSend}
            disabled={!query.trim() || isRunning || isUploading}
            className="p-2 rounded-xl bg-accent text-white hover:opacity-90 disabled:opacity-50 disabled:bg-muted transition-all"
            title="Start Analysis"
          >
            {isRunning ? <Loader2 size={20} className="animate-spin" /> : <Send size={20} />}
          </button>
        </div>
      </div>
    </div>
  );
}
