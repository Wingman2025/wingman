import { useQuery } from '@tanstack/react-query'
import { goalsApi, badgesApi, statsApi } from '../services/api'

const Dashboard = () => {
  const { data: userGoals, isLoading: goalsLoading } = useQuery({
    queryKey: ['userGoals'],
    queryFn: goalsApi.getUserGoals,
    select: (response) => response.data
  })

  const { data: userBadges, isLoading: badgesLoading } = useQuery({
    queryKey: ['userBadges'],
    queryFn: badgesApi.getUserBadges,
    select: (response) => response.data
  })

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['motivationalStats'],
    queryFn: statsApi.getMotivationalStats,
    select: (response) => response.data
  })

  if (goalsLoading || badgesLoading || statsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          ¡Bienvenido a tu Dashboard Motivacional! 🚀
        </h1>
        <p className="text-gray-600">
          Sigue tu progreso, alcanza tus objetivos y desbloquea logros increíbles
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card text-center">
          <div className="text-3xl mb-2">🎯</div>
          <div className="text-2xl font-bold text-primary-600">
            {userGoals?.length || 0}
          </div>
          <div className="text-sm text-gray-600">Objetivos Activos</div>
        </div>
        
        <div className="card text-center">
          <div className="text-3xl mb-2">🏆</div>
          <div className="text-2xl font-bold text-success-600">
            {userBadges?.length || 0}
          </div>
          <div className="text-sm text-gray-600">Logros Desbloqueados</div>
        </div>
        
        <div className="card text-center">
          <div className="text-3xl mb-2">📈</div>
          <div className="text-2xl font-bold text-warning-600">
            {stats?.total_sessions || 0}
          </div>
          <div className="text-sm text-gray-600">Sesiones Totales</div>
        </div>
      </div>

      {/* Active Goals */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4 flex items-center">
          <span className="mr-2">🎯</span>
          Objetivos Activos
        </h2>
        
        {userGoals?.length > 0 ? (
          <div className="space-y-3">
            {userGoals.slice(0, 3).map((goal) => (
              <div key={goal.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex justify-between items-center mb-2">
                  <h3 className="font-medium">{goal.goal_template?.name || goal.custom_goal}</h3>
                  <span className="text-sm text-gray-500">
                    {goal.current_progress}/{goal.target_value}
                  </span>
                </div>
                
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                    style={{ 
                      width: `${Math.min((goal.current_progress / goal.target_value) * 100, 100)}%` 
                    }}
                  ></div>
                </div>
                
                <div className="mt-2 text-sm text-gray-600">
                  {goal.goal_template?.description || 'Objetivo personalizado'}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <div className="text-4xl mb-2">🎯</div>
            <p>No tienes objetivos activos</p>
            <p className="text-sm">¡Crea tu primer objetivo para empezar!</p>
          </div>
        )}
      </div>

      {/* Recent Badges */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4 flex items-center">
          <span className="mr-2">🏆</span>
          Logros Recientes
        </h2>
        
        {userBadges?.length > 0 ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {userBadges.slice(0, 4).map((userBadge) => (
              <div key={userBadge.id} className="text-center p-3 border border-gray-200 rounded-lg">
                <div className="text-3xl mb-2">{userBadge.badge?.icon || '🏆'}</div>
                <div className="text-sm font-medium">{userBadge.badge?.name}</div>
                <div className="text-xs text-gray-500 mt-1">
                  {new Date(userBadge.earned_at).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <div className="text-4xl mb-2">🏆</div>
            <p>Aún no has desbloqueado logros</p>
            <p className="text-sm">¡Completa objetivos para ganar badges!</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default Dashboard
