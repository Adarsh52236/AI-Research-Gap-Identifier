import { ProjectForm } from './ProjectForm';
import { useProjectStore } from '../store/projectStore';
import { Project } from '../types';

interface EditProjectDialogProps {
  isOpen: boolean;
  onClose: () => void;
  project: Project;
}

export function EditProjectDialog({ isOpen, onClose, project }: EditProjectDialogProps) {
  const { updateProject } = useProjectStore();

  if (!isOpen) return null;

  const handleSubmit = async (data: any) => {
    await updateProject(project.id, data);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" onClick={onClose}></div>

        <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        <div className="inline-block align-bottom bg-white rounded-lg px-4 pt-5 pb-4 text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6">
          <div className="mb-5">
            <h3 className="text-lg leading-6 font-medium text-gray-900" id="modal-title">
              Edit Project Settings
            </h3>
          </div>
          
          <ProjectForm 
            initialData={project}
            onSubmit={handleSubmit}
            onCancel={onClose}
            submitLabel="Save Changes"
          />
        </div>
      </div>
    </div>
  );
}
