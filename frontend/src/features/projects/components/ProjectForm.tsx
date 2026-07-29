import { useState } from 'react';
import { ProjectStatus } from '../types';

interface ProjectFormProps {
  initialData?: {
    name: string;
    description: string;
    status?: ProjectStatus;
    tags?: string[];
  };
  onSubmit: (data: {
    name: string;
    description: string;
    status: ProjectStatus;
    tags: string[];
    favorite: boolean;
  }) => Promise<void>;
  onCancel: () => void;
  submitLabel: string;
}

export function ProjectForm({ initialData, onSubmit, onCancel, submitLabel }: ProjectFormProps) {
  const [name, setName] = useState(initialData?.name || '');
  const [description, setDescription] = useState(initialData?.description || '');
  const [status, setStatus] = useState<ProjectStatus>(initialData?.status || ProjectStatus.ACTIVE);
  const [tagsInput, setTagsInput] = useState(initialData?.tags?.join(', ') || '');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (name.length < 3 || name.length > 100) {
      setError('Project name must be between 3 and 100 characters');
      return;
    }

    setIsSubmitting(true);
    setError(null);
    try {
      const tags = tagsInput
        .split(',')
        .map(t => t.trim())
        .filter(t => t.length > 0);
        
      await onSubmit({
        name,
        description,
        status,
        tags,
        favorite: false // Handled separately usually, but default to false for new forms
      });
    } catch (err: any) {
      setError(err.message || 'An error occurred');
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="p-3 text-sm text-red-600 bg-red-50 rounded-md">
          {error}
        </div>
      )}
      
      <div>
        <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">Project Name *</label>
        <input
          id="name"
          type="text"
          required
          minLength={3}
          maxLength={100}
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
          placeholder="e.g. LLM Reasoning Capabilities"
          disabled={isSubmitting}
        />
      </div>

      <div>
        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">Description</label>
        <textarea
          id="description"
          rows={3}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
          placeholder="Briefly describe the goal of this research project..."
          disabled={isSubmitting}
        />
      </div>

      <div>
        <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">Status</label>
        <select
          id="status"
          value={status}
          onChange={(e) => setStatus(e.target.value as ProjectStatus)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
          disabled={isSubmitting}
        >
          <option value={ProjectStatus.ACTIVE}>Active</option>
          <option value={ProjectStatus.COMPLETED}>Completed</option>
          <option value={ProjectStatus.ARCHIVED}>Archived</option>
        </select>
      </div>

      <div>
        <label htmlFor="tags" className="block text-sm font-medium text-gray-700 mb-1">Tags (comma separated)</label>
        <input
          id="tags"
          type="text"
          value={tagsInput}
          onChange={(e) => setTagsInput(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
          placeholder="e.g. ai, medicine, vision"
          disabled={isSubmitting}
        />
      </div>

      <div className="pt-4 flex justify-end gap-3 border-t border-gray-100">
        <button
          type="button"
          onClick={onCancel}
          disabled={isSubmitting}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={isSubmitting}
          className="px-4 py-2 text-sm font-medium text-white bg-primary rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
        >
          {isSubmitting ? 'Saving...' : submitLabel}
        </button>
      </div>
    </form>
  );
}
