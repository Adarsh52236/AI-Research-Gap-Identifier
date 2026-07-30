import { useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { PageContainer } from '@/components/layout/PageContainer';
import { useProjectStore } from '../store/projectStore';
import { ArrowLeft, PlayCircle, Folder, Settings, Tag } from 'lucide-react';
import { AnalysisHistory } from '@/features/analysis/components/AnalysisHistory';

export function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const { getProject, fetchProjects, projects, isLoading } = useProjectStore();

  // If page is loaded directly, we might need to fetch
  useEffect(() => {
    if (projects.length === 0) {
      fetchProjects();
    }
  }, [fetchProjects, projects.length]);

  const project = projectId ? getProject(projectId) : undefined;

  if (isLoading && projects.length === 0) {
    return (
      <PageContainer>
        <div className="flex justify-center items-center py-20 text-gray-400">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mb-4"></div>
          <span className="ml-3">Loading project...</span>
        </div>
      </PageContainer>
    );
  }

  if (!project) {
    return (
      <PageContainer>
        <div className="py-20 text-center">
          <h2 className="text-xl font-bold text-gray-900">Project Not Found</h2>
          <p className="mt-2 text-gray-500">The project you are looking for does not exist or has been deleted.</p>
          <Link to="/projects" className="mt-4 text-primary hover:underline inline-block">
            &larr; Back to Projects
          </Link>
        </div>
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <div className="mb-6">
        <Link to="/projects" className="inline-flex items-center text-sm font-medium text-gray-500 hover:text-gray-700 transition-colors">
          <ArrowLeft className="w-4 h-4 mr-1" />
          Back to Projects
        </Link>
      </div>

      <div className="bg-surface border border-border rounded-xl p-8 mb-8 shadow-sm relative overflow-hidden">
        {/* Decorative background element */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-blue-50 rounded-full blur-3xl -mr-32 -mt-32 opacity-50 pointer-events-none"></div>
        
        <div className="relative z-10 flex flex-col md:flex-row md:items-start justify-between gap-6">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold text-text">{project.name}</h1>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border bg-blue-100 text-blue-800 border-blue-200 capitalize">
                {project.status}
              </span>
            </div>
            
            <p className="text-gray-600 text-lg max-w-3xl mb-6">
              {project.description || 'No description provided for this project.'}
            </p>

            <div className="flex flex-wrap items-center gap-6 text-sm text-gray-500 mb-6">
              <div className="flex items-center">
                <Folder className="w-4 h-4 mr-2" />
                {project.analysisCount} Analyses saved
              </div>
              <div className="flex items-center">
                <Tag className="w-4 h-4 mr-2" />
                {project.tags.length} Tags
              </div>
              <div>
                Created on {new Date(project.createdAt).toLocaleDateString()}
              </div>
            </div>
            
            <div className="flex flex-wrap gap-2">
              {project.tags.map((tag, i) => (
                <span key={i} className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800 border border-gray-200">
                  {tag}
                </span>
              ))}
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-3 md:mt-0 mt-4">
            <button 
              onClick={() => navigate(`/analysis?projectId=${project.id}`)}
              className="inline-flex items-center justify-center px-5 py-2.5 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
            >
              <PlayCircle className="w-4 h-4 mr-2" />
              Run Analysis
            </button>
            <button className="inline-flex items-center justify-center px-4 py-2.5 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary">
              <Settings className="w-4 h-4 mr-2" />
              Settings
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          <section className="bg-surface border border-border rounded-xl p-6 shadow-sm">
            <h2 className="text-xl font-bold text-text mb-4">Recent Analyses</h2>
            <AnalysisHistory projectId={project.id} />
          </section>

          <section className="bg-surface border border-border rounded-xl p-6 shadow-sm">
            <h2 className="text-xl font-bold text-text mb-4">Synthesized Research Gaps</h2>
            <div className="text-center py-10 bg-gray-50 rounded-lg">
              <p className="text-gray-500 text-sm">Research gaps will appear here once you run an analysis.</p>
            </div>
          </section>
        </div>

        <div className="space-y-8">
          <section className="bg-surface border border-border rounded-xl p-6 shadow-sm">
            <h2 className="text-lg font-bold text-text mb-4">Reports</h2>
            <div className="text-center py-8 bg-gray-50 rounded-lg">
              <p className="text-gray-500 text-sm">No PDF reports generated.</p>
            </div>
          </section>

          <section className="bg-surface border border-border rounded-xl p-6 shadow-sm">
            <h2 className="text-lg font-bold text-text mb-4">Project Notes</h2>
            <textarea 
              className="w-full h-32 p-3 border border-gray-300 rounded-md focus:ring-primary focus:border-primary text-sm"
              placeholder="Add your own notes, hypotheses, or reminders here..."
            ></textarea>
          </section>
        </div>
      </div>
    </PageContainer>
  );
}
