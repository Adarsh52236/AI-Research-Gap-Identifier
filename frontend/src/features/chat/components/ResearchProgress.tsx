import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, Loader2, Search, Brain, FileText, Database, Sparkles, ChevronDown, ChevronUp } from 'lucide-react';

interface ResearchProgressProps {
  isResearching: boolean;
}

const STEPS = [
  { id: 1, label: 'Reading document...', icon: FileText, desc: 'Parsing IEEE formatting and extracting text blocks.' },
  { id: 2, label: 'Extracting topics...', icon: Database, desc: 'Running BERTopic clustering to group concepts.' },
  { id: 3, label: 'Comparing literature...', icon: Search, desc: 'Searching embeddings against existing papers.' },
  { id: 4, label: 'Identifying research gaps...', icon: Brain, desc: 'LLM reasoning to find unaddressed problems.' },
  { id: 5, label: 'Generating suggestions...', icon: Sparkles, desc: 'Synthesizing final actionable insights.' }
];

export function ResearchProgress({ isResearching }: ResearchProgressProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [isExpanded, setIsExpanded] = useState(true);
  const [hasCompleted, setHasCompleted] = useState(false);

  useEffect(() => {
    if (isResearching) {
      setHasCompleted(false);
      setIsExpanded(true);
      setCurrentStep(0);
      
      // Simulate progress over time (total ~15-20 seconds)
      const timeouts = [
        setTimeout(() => setCurrentStep(1), 2000),
        setTimeout(() => setCurrentStep(2), 5000),
        setTimeout(() => setCurrentStep(3), 10000),
        setTimeout(() => setCurrentStep(4), 16000),
      ];
      
      return () => timeouts.forEach(clearTimeout);
    } else if (!isResearching && currentStep > 0) {
      // Backend returned! Jump to complete
      setCurrentStep(5);
      setHasCompleted(true);
      
      // Auto collapse after a short delay
      const collapseTimeout = setTimeout(() => {
        setIsExpanded(false);
      }, 1500);
      
      return () => clearTimeout(collapseTimeout);
    }
  }, [isResearching]);

  if (!isResearching && !hasCompleted) return null;

  return (
    <div className="w-full max-w-2xl mx-auto my-6">
      <div className="bg-white border border-border rounded-2xl overflow-hidden shadow-sm transition-all duration-300">
        
        {/* Header / Pill state */}
        <button 
          onClick={() => setIsExpanded(!isExpanded)}
          className="w-full px-5 py-3 flex items-center justify-between bg-gray-50/50 hover:bg-gray-50 transition-colors cursor-pointer"
        >
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-primary">
               {hasCompleted ? <CheckCircle2 className="w-4 h-4" /> : <Search className="w-4 h-4 animate-pulse" />}
            </div>
            <div className="text-sm font-semibold text-text">
              {hasCompleted ? 'Analysis complete — 5 steps' : 'Analyzing paper...'}
            </div>
          </div>
          {isExpanded ? <ChevronUp className="w-4 h-4 text-muted" /> : <ChevronDown className="w-4 h-4 text-muted" />}
        </button>

        {/* Expanded Steps */}
        <AnimatePresence initial={false}>
          {isExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3, ease: 'easeInOut' }}
              className="overflow-hidden"
            >
              <div className="p-5 pt-2 relative">
                {/* Vertical connecting line */}
                <div className="absolute left-9 top-6 bottom-8 w-0.5 bg-gray-100 z-0" />
                
                <div className="space-y-6 relative z-10">
                  {STEPS.map((step, idx) => {
                    const isActive = currentStep === idx;
                    const isDone = currentStep > idx || hasCompleted;
                    const Icon = step.icon;
                    
                    return (
                      <motion.div 
                        key={step.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ 
                          opacity: isActive || isDone ? 1 : 0.4,
                          y: 0 
                        }}
                        transition={{ duration: 0.4, delay: idx * 0.1 }}
                        className="flex gap-4"
                      >
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 bg-white border-2 transition-colors duration-300 ${
                          isDone 
                            ? 'border-green-500 text-green-500' 
                            : isActive 
                              ? 'border-primary text-primary' 
                              : 'border-gray-200 text-gray-300'
                        }`}>
                          {isDone ? (
                            <CheckCircle2 className="w-4 h-4" />
                          ) : isActive ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : (
                            <Icon className="w-4 h-4" />
                          )}
                        </div>
                        
                        <div className="flex-1 pt-1">
                          <div className={`text-sm font-medium transition-colors ${isActive ? 'text-primary' : isDone ? 'text-text' : 'text-muted'}`}>
                            {step.label}
                          </div>
                          
                          {isActive && !isDone && (
                            <motion.div 
                              initial={{ opacity: 0 }}
                              animate={{ opacity: 1 }}
                              className="text-xs text-muted mt-1 animate-pulse"
                            >
                              {step.desc}
                            </motion.div>
                          )}
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
