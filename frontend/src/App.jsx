import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import Analysis from './pages/Analysis';
import Results from './pages/Results';
import NotFound from './pages/NotFound';

// Main App Component with React Router v6
export default function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50 flex flex-col">
        <header className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16 items-center">
              <div className="flex-shrink-0 flex items-center">
                <span className="text-xl font-bold text-blue-600">Research Gap Finder</span>
              </div>
              <nav className="flex space-x-8">
                <a href="/" className="text-gray-600 hover:text-gray-900 font-medium">Search</a>
                <a href="/results" className="text-gray-600 hover:text-gray-900 font-medium">Results</a>
                <a href="/analysis" className="text-gray-600 hover:text-gray-900 font-medium">Analysis</a>
                <a href="/dashboard" className="text-gray-600 hover:text-gray-900 font-medium">Dashboard</a>
              </nav>
            </div>
          </div>
        </header>
        
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/analysis" element={<Analysis />} />
            <Route path="/results" element={<Results />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}
