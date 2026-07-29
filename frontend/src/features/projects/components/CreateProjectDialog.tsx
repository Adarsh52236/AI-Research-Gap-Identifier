import { ProjectForm } from './ProjectForm';
import { useProjectStore } from '../store/projectStore';

interface CreateProjectDialogProps {
  isOpen: boolean;
  onClose: () => void;
}

export function CreateProjectDialog({ isOpen, onClose }: CreateProjectDialogProps) {
  const { createProject } = useProjectStore();

  if (!isOpen) return null;

  const handleSubmit = async (data: any) => {
    await createProject(data);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        {/* Background overlay */}
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" onClick={onClose}></div>

        {/* Modal panel */}
        <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        <div className="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
          <div className="mb-5">
            <h3 className="text-lg leading-6 font-medium text-gray-900" id="modal-title">
              Create New Project
            </h3>
            <p className="text-sm text-gray-500 mt-1">
              Organize your AI research analyses into a central workspace.
            </p>
          </div>
          
          <ProjectForm 
            onSubmit={handleSubmit}
            onCancel={onClose}
            submitLabel="Create Project"
          />
        </div>
      </div>
    </div>
  );
}
