import React, { useState } from 'react';
import { Paperclip, Loader2, Download, AlertTriangle } from 'lucide-react';
import { reviewService } from '../services/reviewService';

export default function ReviewDashboard() {
  const [file, setFile] = useState(null);
  const [prompt, setPrompt] = useState('');
  const [styleGuide, setStyleGuide] = useState('');
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setIsSubmitting(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);
    if (prompt) formData.append('prompt', prompt);
    if (styleGuide) formData.append('style_guide', styleGuide);

    try {
      const res = await reviewService.annotateReview(formData);
      setResult(res);
    } catch (err) {
      setError(err.message || 'Failed to generate review.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-transparent text-text overflow-y-auto">
      <div className="max-w-3xl w-full mx-auto px-6 py-12">
        <h1 className="text-3xl font-serif mb-2 text-text">Annotated Peer-Review Generator</h1>
        <p className="text-muted mb-8 font-serif">
          Upload your research paper to receive professional reviewer annotations overlaid on a fresh PDF.
          <span className="block text-xs text-muted/70 mt-2">API: {import.meta.env.VITE_API_BASE_URL || 'None'}</span>
        </p>
        
        <form onSubmit={handleSubmit} className="bg-panel rounded-2xl shadow-sm border border-border p-8 mb-8">
          <div className="mb-6">
            <label className="block text-sm font-medium text-text mb-2">Research Paper (PDF)</label>
            <div className="flex items-center justify-center w-full">
                <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-border border-dashed rounded-xl cursor-pointer bg-bg hover:bg-border/50 transition-colors">
                    <div className="flex flex-col items-center justify-center pt-5 pb-6">
                        <Paperclip className="w-8 h-8 text-muted mb-2" />
                        <p className="mb-2 text-sm text-muted font-serif">
                          <span className="font-semibold">Click to upload</span> or drag and drop
                        </p>
                        <p className="text-xs text-muted font-serif">{file ? file.name : 'PDF up to 50MB'}</p>
                    </div>
                    <input type="file" className="hidden" accept=".pdf" onChange={handleFileChange} />
                </label>
            </div>
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-text mb-2">Focus Prompt (Optional)</label>
            <textarea
              value={prompt}
              onChange={e => setPrompt(e.target.value)}
              placeholder="E.g., Focus heavily on evaluating the dataset methodology..."
              className="w-full px-4 py-3 rounded-xl border border-border focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent font-serif bg-bg text-text resize-none"
              rows="3"
            />
          </div>
          
          <div className="mb-8">
            <label className="block text-sm font-medium text-text mb-2">Style Guide (Optional)</label>
            <input
              type="text"
              value={styleGuide}
              onChange={e => setStyleGuide(e.target.value)}
              placeholder="E.g., IEEE, ACM, APA"
              className="w-full px-4 py-3 rounded-xl border border-border focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent font-serif bg-bg text-text"
            />
          </div>

          <button
            type="submit"
            disabled={!file || isSubmitting}
            className="w-full py-3 px-4 bg-accent hover:bg-accent/90 text-text rounded-xl font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Generating Review (This usually takes 1-2 minutes)...
              </>
            ) : (
              'Generate Annotated Review'
            )}
          </button>
        </form>

        {error && (
          <div className="p-4 bg-red-900/20 border border-red-500/50 rounded-xl flex items-start text-red-400 mb-8">
            <AlertTriangle className="w-5 h-5 mr-3 mt-0.5 flex-shrink-0" />
            <div>
              <h3 className="font-semibold text-sm">Review Failed</h3>
              <p className="text-sm mt-1">{error}</p>
            </div>
          </div>
        )}

        {result && (
          <div className="p-8 bg-panel border border-border shadow-sm rounded-xl mb-8 flex flex-col items-center text-center">
            <div className="w-16 h-16 bg-accent/20 text-accent rounded-full flex items-center justify-center mb-4">
              <Download className="w-8 h-8" />
            </div>
            <h2 className="text-2xl font-serif mb-2 text-text">Review Complete!</h2>
            <p className="text-muted font-serif mb-6">
              We identified <b className="text-text">{result.issues_count}</b> issues. 
              {result.dropped_count > 0 && ` (Dropped ${result.dropped_count} unlocatable/hallucinated items).`}
            </p>
            
            {result.notes && (
              <p className="text-accent bg-accent-soft px-4 py-2 rounded-lg text-sm mb-6 max-w-lg">
                {result.notes}
              </p>
            )}

            <a 
              href={reviewService.getDownloadUrl(result.review_run_id)} 
              download="Research_Paper_Annotated_Issues_Solutions.pdf"
              target="_blank"
              rel="noreferrer"
              className="py-3 px-6 bg-accent hover:bg-accent/90 text-text rounded-xl font-medium transition-colors"
            >
              Download Annotated PDF
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
