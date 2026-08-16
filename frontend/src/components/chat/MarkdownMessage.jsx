import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/atom-one-dark.css';

export default function MarkdownMessage({ content }) {
  return (
    <div className="prose prose-invert max-w-none leading-relaxed text-base font-serif">
      <ReactMarkdown 
        remarkPlugins={[remarkGfm]} 
        rehypePlugins={[rehypeHighlight]}
        components={{
          code({node, inline, className, children, ...props}) {
            return !inline ? (
              <div className="relative group rounded-md overflow-hidden my-4 shadow-sm border border-border">
                <div className="flex justify-between items-center bg-gray-800 text-gray-400 px-3 py-1 text-xs font-sans">
                  <span>Code</span>
                  <button 
                    onClick={() => navigator.clipboard.writeText(String(children).replace(/\n$/, ''))}
                    className="hover:text-white transition-colors opacity-0 group-hover:opacity-100"
                  >
                    Copy
                  </button>
                </div>
                <div className="bg-gray-900 p-4 overflow-x-auto text-sm font-mono text-gray-100">
                  <code className={className} {...props}>
                    {children}
                  </code>
                </div>
              </div>
            ) : (
              <code className="bg-border/50 text-text px-1.5 py-0.5 rounded-md text-sm font-mono" {...props}>
                {children}
              </code>
            )
          },
          table({children}) {
            return (
              <div className="overflow-x-auto my-6 border border-border rounded-lg shadow-sm">
                <table className="min-w-full divide-y divide-border text-sm font-sans">{children}</table>
              </div>
            );
          },
          thead({children}) {
            return <thead className="bg-panel">{children}</thead>;
          },
          th({children}) {
            return <th className="px-4 py-3 text-left font-medium text-muted uppercase tracking-wider">{children}</th>;
          },
          td({children}) {
            return <td className="px-4 py-3 text-text border-t border-border">{children}</td>;
          }
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
