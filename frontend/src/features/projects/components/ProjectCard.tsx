import { Link } from 'react-router-dom';
import { Project, ProjectStatus } from '../types';
import { useState } from 'react';
import { EditProjectDialog } from './EditProjectDialog';
import { DeleteProjectDialog } from './DeleteProjectDialog';
import { MoreVertical, Folder, Clock, Hash, Edit2, Archive, Trash2 } from 'lucide-react';

interface ProjectCardProps {
  project: Project;
}

export function ProjectCard({ project }: ProjectCardProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);

  const getStatusColor = (status: ProjectStatus) => {
    switch (status) {
      case ProjectStatus.ACTIVE: return 'bg-emerald-100 text-emerald-800 border-emerald-200';
      case ProjectStatus.COMPLETED: return 'bg-blue-100 text-blue-800 border-blue-200';
      case ProjectStatus.ARCHIVED: return 'bg-gray-100 text-gray-800 border-gray-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <>
      <div className="bg-surface rounded-xl shadow-sm border border-border p-6 hover:border-primary/50 transition-all flex flex-col h-full relative group">
        
        <div className="flex justify-between items-start mb-4">
          <Link to={`/projects/${project.id}`} className="flex-1 min-w-0 pr-4">
            <h3 className="text-xl font-bold text-text truncate group-hover:text-primary transition-colors">
              {project.name}
            </h3>
          </Link>
          
          <div className="relative">
            <button 
              onClick={(e) => {
                e.preventDefault();
                setIsMenuOpen(!isMenuOpen);
              }}
              className="text-gray-400 hover:text-gray-600 focus:outline-none p-1 rounded-full hover:bg-gray-100"
            >
              <MoreVertical className="w-5 h-5" />
            </button>

            {isMenuOpen && (
              <div className="absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-10">
                <div className="py-1" role="menu">
                  <button
                    onClick={() => { setIsEditOpen(true); setIsMenuOpen(false); }}
                    className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center"
                  >
                    <Edit2 className="w-4 h-4 mr-2" /> Edit Project
                  </button>
                  <button
                    onClick={() => { setIsMenuOpen(false); /* Archive logic */ }}
                    className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center"
                  >
                    <Archive className="w-4 h-4 mr-2" /> Archive (Placeholder)
                  </button>
                  <button
                    onClick={() => { setIsDeleteOpen(true); setIsMenuOpen(false); }}
                    className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center"
                  >
                    <Trash2 className="w-4 h-4 mr-2" /> Delete
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        <Link to={`/projects/${project.id}`} className="flex-1 flex flex-col">
          <p className="text-muted text-sm line-clamp-2 mb-4 flex-1">
            {project.description || 'No description provided.'}
          </p>

          <div className="flex flex-wrap gap-2 mb-4">
            {project.tags.slice(0, 3).map((tag, idx) => (
              <span key={idx} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                <Hash className="w-3 h-3 mr-1" />
                {tag}
              </span>
            ))}
            {project.tags.length > 3 && (
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                +{project.tags.length - 3} more
              </span>
            )}
          </div>

          <div className="mt-auto pt-4 border-t border-border flex items-center justify-between">
            <div className="flex flex-col">
              <span className="text-xs text-gray-400 flex items-center mb-1">
                <Clock className="w-3 h-3 mr-1" />
                Created {new Date(project.createdAt).toLocaleDateString()}
              </span>
              <span className="text-xs font-medium text-gray-600 flex items-center">
                <Folder className="w-3 h-3 mr-1" />
                {project.analysisCount} Analyses
              </span>
            </div>
            
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border capitalize ${getStatusColor(project.status)}`}>
              {project.status}
            </span>
          </div>
        </Link>
      </div>

      <EditProjectDialog isOpen={isEditOpen} onClose={() => setIsEditOpen(false)} project={project} />
      <DeleteProjectDialog isOpen={isDeleteOpen} onClose={() => setIsDeleteOpen(false)} project={project} />
    </>
  );
}
