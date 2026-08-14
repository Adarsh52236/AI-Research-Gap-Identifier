import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import useAppStore from '../store/useAppStore';
import { downloadPaper, extractPaper } from '../services/papersService';

export default function Results() {
  const { results, query, downloads, extractions, setDownload, setExtraction, togglePaperSelection, selectedPaperIds, selectAllPapers } = useAppStore();
  const [processing, setProcessing] = useState({});
  const navigate = useNavigate();

  const handleProcess = async (paper) => {
    setProcessing(prev => ({ ...prev, [paper.paper_id]: true }));
    try {
      // 1. Download
      let localPath = downloads[paper.paper_id];
      if (!localPath && paper.pdf_url) {
        const dlRes = await downloadPaper(paper.pdf_url, paper.paper_id, paper.source, paper.title, paper.year);
        localPath = dlRes.local_path;
        setDownload(paper.paper_id, localPath);
      }
      
      // 2. Extract
      if (localPath && !extractions[paper.paper_id]) {
        const exRes = await extractPaper(localPath, paper.paper_id, paper.source, paper.year);
        setExtraction(paper.paper_id, exRes.sections_found || []);
      }
      
      // Select it automatically for analysis
      if (!selectedPaperIds.includes(paper.paper_id)) {
        togglePaperSelection(paper.paper_id);
      }
    } catch (err) {
      console.error('Processing failed', err);
      alert('Failed to process ' + paper.title);
    } finally {
      setProcessing(prev => ({ ...prev, [paper.paper_id]: false }));
    }
  };

  const hasResults = results && results.length > 0;

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Search Results</h1>
          {query && <p className="text-gray-500">Query: "{query}"</p>}
        </div>
        <div className="space-x-4">
          <Link to="/" className="text-blue-600 hover:underline">New Search</Link>
          <button 
            onClick={() => navigate('/analysis')}
            disabled={selectedPaperIds.length === 0}
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:opacity-50"
          >
            Go to Analysis ({selectedPaperIds.length})
          </button>
        </div>
      </div>

      {!hasResults ? (
        <div className="bg-gray-50 p-8 text-center rounded text-gray-500">
          No results found. Try a different search.
        </div>
      ) : (
        <div className="space-y-4">
          {results.map(paper => {
            const isProcessing = processing[paper.paper_id];
            const isDownloaded = !!downloads[paper.paper_id];
            const isExtracted = !!extractions[paper.paper_id];
            const isSelected = selectedPaperIds.includes(paper.paper_id);

            return (
              <div key={paper.paper_id} className="border border-gray-200 rounded p-4 bg-white shadow-sm flex items-start">
                <div className="mr-4 mt-1">
                  <input 
                    type="checkbox"
                    checked={isSelected}
                    onChange={() => togglePaperSelection(paper.paper_id)}
                    className="w-5 h-5 text-blue-600 rounded focus:ring-blue-500"
                    disabled={!isExtracted}
                  />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-lg text-gray-800 mb-1">{paper.title}</h3>
                  <div className="text-sm text-gray-500 mb-2">
                    {paper.year || 'Unknown Year'} • {paper.source} 
                  </div>
                  {paper.pdf_url ? (
                    <a href={paper.pdf_url} target="_blank" rel="noreferrer" className="text-blue-500 hover:underline text-sm mb-3 inline-block">
                      View Original PDF
                    </a>
                  ) : (
                    <span className="text-gray-400 text-sm mb-3 inline-block">No PDF Available</span>
                  )}
                  
                  <div className="flex items-center space-x-3 mt-2">
                    <button
                      onClick={() => handleProcess(paper)}
                      disabled={isProcessing || !paper.pdf_url || (isDownloaded && isExtracted)}
                      className="text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-1.5 rounded disabled:opacity-50"
                    >
                      {isProcessing ? 'Processing...' : (isDownloaded && isExtracted ? 'Processed' : 'Download & Extract')}
                    </button>
                    {isDownloaded && <span className="text-xs text-green-600 bg-green-50 px-2 py-1 rounded">Downloaded</span>}
                    {isExtracted && <span className="text-xs text-green-600 bg-green-50 px-2 py-1 rounded">Extracted</span>}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
