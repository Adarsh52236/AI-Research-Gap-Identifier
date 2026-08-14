import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, BookOpen } from 'lucide-react';

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-bg text-text flex flex-col items-center justify-center p-6 relative overflow-hidden transition-colors duration-300">
      {/* Decorative background elements */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-accentSoft rounded-full mix-blend-multiply filter blur-3xl opacity-50 dark:opacity-10"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-accentSoft rounded-full mix-blend-multiply filter blur-3xl opacity-50 dark:opacity-10"></div>

      <div className="max-w-3xl text-center z-10 flex flex-col items-center">
        <div className="w-16 h-16 bg-panel shadow-sm border border-border rounded-2xl flex items-center justify-center mb-8 text-accent">
          <BookOpen size={32} />
        </div>
        <h1 className="text-5xl sm:text-6xl font-serif font-medium tracking-tight mb-6 text-text">
          Discover the unexplored.
        </h1>
        <p className="text-lg sm:text-xl text-muted max-w-2xl leading-relaxed mb-10 font-sans">
          An AI-powered research assistant that analyzes thousands of papers to identify structural gaps, contradictory findings, and novel opportunities in any domain.
        </p>
        <button 
          onClick={() => navigate('/app')}
          className="flex items-center gap-2 bg-accent text-white px-8 py-4 rounded-full font-medium hover:scale-105 hover:shadow-lg transition-all duration-300 shadow-sm"
        >
          Start analysis
          <ArrowRight size={20} />
        </button>
      </div>
    </div>
  );
}
