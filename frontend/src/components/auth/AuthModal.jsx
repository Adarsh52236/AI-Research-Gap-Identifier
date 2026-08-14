import React, { useState } from 'react';
import { authService } from '../../services/authService';
import useAppStore from '../../store/useAppStore';
import { Loader2, X } from 'lucide-react';

export default function AuthModal({ isOpen, onClose }) {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAppStore();

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!isLogin && password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    setLoading(true);
    try {
      if (isLogin) {
        const res = await authService.login(username, password);
        login(res.access_token, { username });
        onClose();
      } else {
        await authService.signup(username, email, password);
        const res = await authService.login(username, password);
        login(res.access_token, { username });
        onClose();
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-panel rounded-2xl w-full max-w-md shadow-xl border border-border p-6 relative">
        <button onClick={onClose} className="absolute right-4 top-4 text-muted hover:text-text">
          <X size={20} />
        </button>
        <h2 className="text-2xl font-serif text-text mb-6">
          {isLogin ? 'Welcome Back' : 'Create Account'}
        </h2>
        
        {error && <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-lg text-sm">{error}</div>}
        
        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <div>
              <label className="block text-sm font-medium text-text mb-1">Email</label>
              <input 
                type="email" 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-bg border border-border rounded-lg px-4 py-2 focus:outline-none focus:border-accent text-text"
                required
              />
            </div>
          )}
          <div>
            <label className="block text-sm font-medium text-text mb-1">Username</label>
            <input 
              type="text" 
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full bg-bg border border-border rounded-lg px-4 py-2 focus:outline-none focus:border-accent text-text"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-text mb-1">Password</label>
            <input 
              type="password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-bg border border-border rounded-lg px-4 py-2 focus:outline-none focus:border-accent text-text"
              required
            />
          </div>
          {!isLogin && (
            <div>
              <label className="block text-sm font-medium text-text mb-1">Confirm Password</label>
              <input 
                type="password" 
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full bg-bg border border-border rounded-lg px-4 py-2 focus:outline-none focus:border-accent text-text"
                required
              />
            </div>
          )}
          
          <button 
            type="submit" 
            disabled={loading}
            className="w-full bg-accent text-white rounded-lg py-2 font-medium hover:opacity-90 disabled:opacity-50 flex justify-center mt-2"
          >
            {loading ? <Loader2 className="animate-spin" /> : (isLogin ? 'Log In' : 'Sign Up')}
          </button>
        </form>
        
        <div className="mt-4 text-center text-sm text-muted">
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <button onClick={() => {
            setIsLogin(!isLogin);
            setError('');
          }} className="text-accent hover:underline">
            {isLogin ? 'Sign up' : 'Log in'}
          </button>
        </div>
      </div>
    </div>
  );
}
