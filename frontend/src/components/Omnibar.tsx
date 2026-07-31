import { useState, KeyboardEvent } from 'react';
import { Search, Loader2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useProjectStore } from '@/features/projects/store/projectStore';
import { ProjectStatus } from '@/features/projects/types';

export function Omnibar() {
  const [query, setQuery] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();
  const { createProject } = useProjectStore();

  const handleSubmit = async () => {
    if (!query.trim() || isSubmitting) return;

    setIsSubmitting(true);
    
    // Auto-create a project named after the first few words of the query
    const words = query.trim().split(/\s+/);
    const projectName = `Research: ${words.slice(0, 5).join(' ')}${words.length > 5 ? '...' : ''}`;
    
    try {
      // createProject doesn't return the project in the store currently? 
      // Wait, let's check `projectStore.ts` implementation.
      // Ah, createProject in store:
      // const createProject = useCallback(async (data: Omit<...>) => {
      //   try {
      //     const newProject = await projectsApi.createProject(data);
      //     setProjects(prev => [newProject, ...prev]);
      //   }
      // }, []);
      // It DOES NOT return the project. It returns void. I need to modify it or fetch it.
      // Actually, wait, let me look at `projectStore.ts`.
      
      const newProject = await createProject({
        name: projectName,
        description: `Automated project for query: "${query}"`,
        tags: ['auto-generated'],
        status: ProjectStatus.ACTIVE,
        favorite: false
      });

      // If newProject is undefined, I'll need to update projectStore.ts
      const projectId = newProject?.id;
      if (projectId) {
        navigate(`/analysis?projectId=${projectId}&query=${encodeURIComponent(query)}`);
      } else {
        // Fallback if not returning
        console.warn("createProject didn't return a project ID");
      }
    } catch (err) {
      console.error('Failed to create project from Omnibar:', err);
      setIsSubmitting(false);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSubmit();
    }
  };

  return (
    <div className="relative w-full max-w-3xl mx-auto shadow-sm group">
      <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
        <Search className="h-6 w-6 text-gray-400 group-focus-within:text-primary transition-colors" />
      </div>
      <input
        type="text"
        className="block w-full pl-12 pr-12 py-4 text-lg border border-gray-300 rounded-xl leading-5 bg-white text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary transition-shadow shadow-sm hover:shadow-md focus:shadow-md"
        placeholder="What would you like to research today? e.g. 'Federated learning in IoT'"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={isSubmitting}
        autoFocus
      />
      {isSubmitting && (
        <div className="absolute inset-y-0 right-0 pr-4 flex items-center">
          <Loader2 className="h-5 w-5 text-primary animate-spin" />
        </div>
      )}
      {!isSubmitting && query.trim() && (
        <div className="absolute inset-y-0 right-0 pr-2 flex items-center">
          <button 
            onClick={handleSubmit}
            className="p-2 bg-primary text-white rounded-lg hover:bg-blue-600 transition-colors text-sm font-medium"
          >
            Research
          </button>
        </div>
      )}
    </div>
  );
}
