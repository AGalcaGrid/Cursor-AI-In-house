import { useEffect, useState } from 'react';
import type { Task } from '../types/project';
import type { TeamMember } from '../types/team';
import ProjectOverview from './ProjectOverview';
import TeamMembers from './TeamMembers';
import ProgressChart from './ProgressChart';
import ActivityFeed from './ActivityFeed';
import QuickActions from './QuickActions';
import { useTeamDashboard } from '../../context/TeamDashboardContext';
import { useTheme } from '../../context/ThemeContext';
import { X, Sun, Moon } from 'lucide-react';

export default function TeamDashboard() {
  const {
    data,
    isLoading,
    error,
    selectedProject,
    loadDashboardData,
    setSelectedProject,
    addTeamMember,
    createTask,
    updateTaskStatus,
  } = useTeamDashboard();
  
  const { theme, toggleTheme } = useTheme();
  
  // Modal states
  const [showCreateTaskModal, setShowCreateTaskModal] = useState(false);
  const [showInviteMemberModal, setShowInviteMemberModal] = useState(false);
  const [newTaskData, setNewTaskData] = useState({ title: '', description: '', projectId: 0 });
  const [newMemberData, setNewMemberData] = useState<{ name: string; email: string; role: TeamMember['role'] }>({ name: '', email: '', role: 'developer' });

  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  const handleCreateTask = () => {
    if (data?.projects.length) {
      setNewTaskData({ title: '', description: '', projectId: data.projects[0].id });
      setShowCreateTaskModal(true);
    }
  };

  const handleSubmitTask = () => {
    if (newTaskData.title && newTaskData.projectId) {
      createTask(newTaskData.projectId, {
        title: newTaskData.title,
        description: newTaskData.description,
        status: 'todo',
        priority: 'medium',
      });
      setShowCreateTaskModal(false);
      setNewTaskData({ title: '', description: '', projectId: 0 });
    }
  };

  const handleCreateProject = () => {
    console.log('Create project clicked');
  };

  const handleInviteMember = () => {
    setNewMemberData({ name: '', email: '', role: 'developer' });
    setShowInviteMemberModal(true);
  };

  const handleSubmitMember = () => {
    if (newMemberData.name && newMemberData.email) {
      const newMember: TeamMember = {
        id: Date.now(),
        name: newMemberData.name,
        email: newMemberData.email,
        role: newMemberData.role,
        status: 'online',
        department: 'Engineering',
        tasksCompleted: 0,
        tasksInProgress: 0,
      };
      addTeamMember(newMember);
      setShowInviteMemberModal(false);
      setNewMemberData({ name: '', email: '', role: 'developer' });
    }
  };

  const handleGenerateReport = () => {
    console.log('Generate report clicked');
  };

  const handleTaskStatusChange = (projectId: number, taskId: number, status: Task['status']) => {
    updateTaskStatus(projectId, taskId, status);
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-white rounded-xl shadow-sm p-4 animate-pulse">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gray-200 rounded-lg" />
                <div className="flex-1">
                  <div className="h-6 bg-gray-200 rounded w-16 mb-1" />
                  <div className="h-4 bg-gray-200 rounded w-20" />
                </div>
              </div>
            </div>
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 bg-white rounded-xl shadow-sm p-6 animate-pulse">
            <div className="h-64 bg-gray-200 rounded" />
          </div>
          <div className="bg-white rounded-xl shadow-sm p-6 animate-pulse">
            <div className="h-64 bg-gray-200 rounded" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
        <p className="text-red-700">{error || 'Failed to load data'}</p>
        <button
          onClick={loadDashboardData}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${theme === 'dark' ? 'dark' : ''}`}>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Team Dashboard</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">Welcome back! Here's what's happening with your team.</p>
        </div>
        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
          aria-label="Toggle theme"
        >
          {theme === 'light' ? <Moon className="w-5 h-5" /> : <Sun className="w-5 h-5 text-yellow-400" />}
        </button>
      </div>

      <QuickActions
        onCreateTask={handleCreateTask}
        onCreateProject={handleCreateProject}
        onInviteMember={handleInviteMember}
        onGenerateReport={handleGenerateReport}
      />

      <ProjectOverview
        projects={data.projects}
        stats={data.stats}
        onProjectClick={setSelectedProject}
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ProgressChart
            data={data.weeklyProgress}
            title="Weekly Progress"
            subtitle="Task completion rate this week"
          />
        </div>
        <div>
          <TeamMembers
            members={data.members}
            onMemberClick={(member) => console.log('Member clicked:', member)}
          />
        </div>
      </div>

      <ActivityFeed
        activities={data.activities}
        maxItems={8}
        onViewAll={() => console.log('View all activities')}
      />

      {/* Project Detail Modal */}
      {selectedProject && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">{selectedProject.name}</h2>
                <p className="text-gray-500 dark:text-gray-400 mt-1">{selectedProject.description}</p>
              </div>
              <button
                onClick={() => setSelectedProject(null)}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <h3 className="font-medium text-gray-900 dark:text-white mb-2">Progress</h3>
                <div className="w-full bg-gray-100 dark:bg-gray-700 rounded-full h-3">
                  <div
                    className="h-3 rounded-full"
                    style={{ width: `${selectedProject.progress}%`, backgroundColor: selectedProject.color }}
                  />
                </div>
                <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">{selectedProject.progress}% complete</p>
              </div>
              <div>
                <h3 className="font-medium text-gray-900 dark:text-white mb-2">Tasks ({selectedProject.tasks.length})</h3>
                <div className="space-y-2">
                  {selectedProject.tasks.slice(0, 8).map((task) => (
                    <div key={task.id} className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-700 rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className={`w-2 h-2 rounded-full ${
                          task.status === 'done' ? 'bg-green-500' :
                          task.status === 'in_progress' ? 'bg-blue-500' :
                          task.status === 'review' ? 'bg-yellow-500' : 'bg-gray-400'
                        }`} />
                        <span className="text-sm text-gray-700 dark:text-gray-300">{task.title}</span>
                      </div>
                      {task.status !== 'done' && (
                        <button
                          onClick={() => handleTaskStatusChange(selectedProject.id, task.id, 'done')}
                          className="text-xs px-2 py-1 bg-green-100 text-green-700 rounded hover:bg-green-200 transition-colors"
                        >
                          Complete
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create Task Modal */}
      {showCreateTaskModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">Create New Task</h2>
              <button
                onClick={() => setShowCreateTaskModal(false)}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Project</label>
                <select
                  value={newTaskData.projectId}
                  onChange={(e) => setNewTaskData({ ...newTaskData, projectId: Number(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
                >
                  {data?.projects.map((project) => (
                    <option key={project.id} value={project.id}>{project.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Task Title</label>
                <input
                  type="text"
                  value={newTaskData.title}
                  onChange={(e) => setNewTaskData({ ...newTaskData, title: e.target.value })}
                  placeholder="Enter task title"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Description</label>
                <textarea
                  value={newTaskData.description}
                  onChange={(e) => setNewTaskData({ ...newTaskData, description: e.target.value })}
                  placeholder="Enter task description"
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
                />
              </div>
              <button
                onClick={handleSubmitTask}
                disabled={!newTaskData.title}
                className="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Create Task
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Invite Member Modal */}
      {showInviteMemberModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">Invite Team Member</h2>
              <button
                onClick={() => setShowInviteMemberModal(false)}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Name</label>
                <input
                  type="text"
                  value={newMemberData.name}
                  onChange={(e) => setNewMemberData({ ...newMemberData, name: e.target.value })}
                  placeholder="Enter name"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Email</label>
                <input
                  type="email"
                  value={newMemberData.email}
                  onChange={(e) => setNewMemberData({ ...newMemberData, email: e.target.value })}
                  placeholder="Enter email"
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Role</label>
                <select
                  value={newMemberData.role}
                  onChange={(e) => setNewMemberData({ ...newMemberData, role: e.target.value as TeamMember['role'] })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
                >
                  <option value="developer">Developer</option>
                  <option value="designer">Designer</option>
                  <option value="manager">Manager</option>
                  <option value="qa">QA</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
              <button
                onClick={handleSubmitMember}
                disabled={!newMemberData.name || !newMemberData.email}
                className="w-full py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Add Member
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
