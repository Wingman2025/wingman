import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { goalsApi } from '../services/api'

const Goals = () => {
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [newGoal, setNewGoal] = useState({
    template_id: '',
    custom_goal: '',
    target_value: '',
    unit: ''
  })

  const queryClient = useQueryClient()

  const { data: userGoals, isLoading: goalsLoading } = useQuery({
    queryKey: ['userGoals'],
    queryFn: goalsApi.getUserGoals,
    select: (response) => response.data
  })

  const { data: templates, isLoading: templatesLoading } = useQuery({
    queryKey: ['goalTemplates'],
    queryFn: goalsApi.getGoalTemplates,
    select: (response) => response.data
  })

  const createGoalMutation = useMutation({
    mutationFn: goalsApi.createGoal,
    onSuccess: () => {
      queryClient.invalidateQueries(['userGoals'])
      setShowCreateForm(false)
      setNewGoal({ template_id: '', custom_goal: '', target_value: '', unit: '' })
    }
  })

  const updateProgressMutation = useMutation({
    mutationFn: ({ goalId, progress }) => goalsApi.updateGoalProgress(goalId, progress),
    onSuccess: () => {
      queryClient.invalidateQueries(['userGoals'])
    }
  })

  const handleCreateGoal = (e) => {
    e.preventDefault()
    createGoalMutation.mutate(newGoal)
  }

  const handleProgressUpdate = (goalId, currentProgress, increment = 1) => {
    const newProgress = currentProgress + increment
    updateProgressMutation.mutate({ goalId, progress: newProgress })
  }

  if (goalsLoading || templatesLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Mis Objetivos 🎯</h1>
          <p className="text-gray-600 mt-2">Gestiona y sigue el progreso de tus metas</p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="btn btn-primary"
        >
          + Nuevo Objetivo
        </button>
      </div>

      {/* Create Goal Form */}
      {showCreateForm && (
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">Crear Nuevo Objetivo</h2>
          <form onSubmit={handleCreateGoal} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tipo de Objetivo
              </label>
              <select
                value={newGoal.template_id}
                onChange={(e) => setNewGoal({ ...newGoal, template_id: e.target.value })}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="">Selecciona una plantilla</option>
                {templates?.map((template) => (
                  <option key={template.id} value={template.id}>
                    {template.name} - {template.description}
                  </option>
                ))}
                <option value="custom">Objetivo Personalizado</option>
              </select>
            </div>

            {newGoal.template_id === 'custom' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Objetivo Personalizado
                </label>
                <input
                  type="text"
                  value={newGoal.custom_goal}
                  onChange={(e) => setNewGoal({ ...newGoal, custom_goal: e.target.value })}
                  placeholder="Describe tu objetivo..."
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  required
                />
              </div>
            )}

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Meta
                </label>
                <input
                  type="number"
                  value={newGoal.target_value}
                  onChange={(e) => setNewGoal({ ...newGoal, target_value: e.target.value })}
                  placeholder="100"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Unidad
                </label>
                <input
                  type="text"
                  value={newGoal.unit}
                  onChange={(e) => setNewGoal({ ...newGoal, unit: e.target.value })}
                  placeholder="sesiones, minutos, etc."
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
            </div>

            <div className="flex space-x-3">
              <button
                type="submit"
                disabled={createGoalMutation.isPending}
                className="btn btn-primary"
              >
                {createGoalMutation.isPending ? 'Creando...' : 'Crear Objetivo'}
              </button>
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                className="btn btn-secondary"
              >
                Cancelar
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Goals List */}
      <div className="space-y-4">
        {userGoals?.length > 0 ? (
          userGoals.map((goal) => {
            const progressPercentage = Math.min((goal.current_progress / goal.target_value) * 100, 100)
            const isCompleted = goal.current_progress >= goal.target_value

            return (
              <div key={goal.id} className="card">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {goal.goal_template?.name || goal.custom_goal}
                    </h3>
                    <p className="text-gray-600 text-sm mt-1">
                      {goal.goal_template?.description || 'Objetivo personalizado'}
                    </p>
                  </div>
                  
                  {isCompleted && (
                    <span className="bg-success-100 text-success-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                      ✅ Completado
                    </span>
                  )}
                </div>

                <div className="mb-4">
                  <div className="flex justify-between text-sm text-gray-600 mb-2">
                    <span>Progreso</span>
                    <span>
                      {goal.current_progress} / {goal.target_value} {goal.unit}
                    </span>
                  </div>
                  
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div 
                      className={`h-3 rounded-full transition-all duration-300 ${
                        isCompleted ? 'bg-success-600' : 'bg-primary-600'
                      }`}
                      style={{ width: `${progressPercentage}%` }}
                    ></div>
                  </div>
                  
                  <div className="text-right text-sm text-gray-500 mt-1">
                    {progressPercentage.toFixed(1)}%
                  </div>
                </div>

                {!isCompleted && (
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleProgressUpdate(goal.id, goal.current_progress, 1)}
                      disabled={updateProgressMutation.isPending}
                      className="btn btn-primary text-sm"
                    >
                      +1 {goal.unit}
                    </button>
                    <button
                      onClick={() => handleProgressUpdate(goal.id, goal.current_progress, 5)}
                      disabled={updateProgressMutation.isPending}
                      className="btn btn-secondary text-sm"
                    >
                      +5 {goal.unit}
                    </button>
                  </div>
                )}

                <div className="mt-3 text-xs text-gray-500">
                  Creado: {new Date(goal.created_at).toLocaleDateString()}
                  {goal.completed_at && (
                    <span className="ml-4">
                      Completado: {new Date(goal.completed_at).toLocaleDateString()}
                    </span>
                  )}
                </div>
              </div>
            )
          })
        ) : (
          <div className="card text-center py-12">
            <div className="text-6xl mb-4">🎯</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              No tienes objetivos activos
            </h3>
            <p className="text-gray-600 mb-6">
              ¡Crea tu primer objetivo para comenzar tu journey motivacional!
            </p>
            <button
              onClick={() => setShowCreateForm(true)}
              className="btn btn-primary"
            >
              Crear Mi Primer Objetivo
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default Goals
