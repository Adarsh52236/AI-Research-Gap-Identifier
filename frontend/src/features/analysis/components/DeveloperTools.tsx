import { useState } from 'react';
import { ChevronDown, ChevronUp, Code } from 'lucide-react';

interface DeveloperToolsProps {
  data: any;
}

export function DeveloperTools({ data }: DeveloperToolsProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="bg-surface rounded-xl shadow-sm border border-border mt-8 overflow-hidden">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100 transition-colors focus:outline-none"
      >
        <div className="flex items-center text-gray-700 font-medium">
          <Code className="w-5 h-5 mr-2" />
          Developer Tools: Raw Response
        </div>
        {isOpen ? <ChevronUp className="w-5 h-5 text-gray-500" /> : <ChevronDown className="w-5 h-5 text-gray-500" />}
      </button>
      
      {isOpen && (
        <div className="p-4 border-t border-border bg-gray-900 overflow-x-auto">
          <pre className="text-xs text-green-400 font-mono">
            {JSON.stringify(data, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
