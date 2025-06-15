import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { badgesApi } from '../services/api'

const Badges = () => {
  const queryClient = useQueryClient()

  const { data: userBadges, isLoading: userBadgesLoading } = useQuery({
    queryKey: ['userBadges'],
    queryFn: badgesApi.getUserBadges,
    select: (response) => response.data
  })

  const { data: allBadges, isLoading: allBadgesLoading } = useQuery({
    queryKey: ['allBadges'],
    queryFn: badgesApi.getAllBadges,
    select: (response) => response.data
  })

  const unlockBadgeMutation = useMutation({
    mutationFn: badgesApi.unlockBadge,
    onSuccess: () => {
      queryClient.invalidateQueries(['userBadges'])
    }
  })

  if (userBadgesLoading || allBadgesLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  // Create a map of earned badges for quick lookup
  const earnedBadgeIds = new Set(userBadges?.map(ub => ub.badge_id) || [])

  // Group badges by category
  const badgesByCategory = allBadges?.reduce((acc, badge) => {
    if (!acc[badge.category]) {
      acc[badge.category] = []
    }
    acc[badge.category].push(badge)
    return acc
  }, {}) || {}

  const rarityColors = {
    'common': 'bg-gray-100 text-gray-800 border-gray-300',
    'rare': 'bg-blue-100 text-blue-800 border-blue-300',
    'epic': 'bg-purple-100 text-purple-800 border-purple-300',
    'legendary': 'bg-yellow-100 text-yellow-800 border-yellow-300'
  }

  const categoryIcons = {
    'sessions': '🏃',
    'consistency': '📅',
    'improvement': '📈',
    'milestones': '🎯',
    'special': '⭐'
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Mis Logros 🏆</h1>
        <p className="text-gray-600">
          Colecciona badges completando objetivos y alcanzando hitos especiales
        </p>
        
        <div className="flex justify-center space-x-6 mt-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-success-600">
              {userBadges?.length || 0}
            </div>
            <div className="text-sm text-gray-600">Desbloqueados</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-400">
              {(allBadges?.length || 0) - (userBadges?.length || 0)}
            </div>
            <div className="text-sm text-gray-600">Por Desbloquear</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-primary-600">
              {allBadges?.length || 0}
            </div>
            <div className="text-sm text-gray-600">Total</div>
          </div>
        </div>
      </div>

      {/* Badges by Category */}
      {Object.entries(badgesByCategory).map(([category, badges]) => (
        <div key={category} className="card">
          <h2 className="text-xl font-semibold mb-6 flex items-center">
            <span className="mr-2 text-2xl">
              {categoryIcons[category] || '🏆'}
            </span>
            {category.charAt(0).toUpperCase() + category.slice(1)}
            <span className="ml-2 text-sm text-gray-500">
              ({badges.filter(b => earnedBadgeIds.has(b.id)).length}/{badges.length})
            </span>
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {badges.map((badge) => {
              const isEarned = earnedBadgeIds.has(badge.id)
              const userBadge = userBadges?.find(ub => ub.badge_id === badge.id)
              
              return (
                <div
                  key={badge.id}
                  className={`relative border-2 rounded-xl p-4 transition-all duration-200 ${
                    isEarned
                      ? 'border-success-300 bg-success-50 shadow-md'
                      : 'border-gray-200 bg-gray-50 opacity-75'
                  }`}
                >
                  {/* Rarity Badge */}
                  <div className={`absolute top-2 right-2 px-2 py-1 rounded-full text-xs font-medium border ${
                    rarityColors[badge.rarity] || rarityColors.common
                  }`}>
                    {badge.rarity}
                  </div>

                  {/* Badge Icon */}
                  <div className="text-center mb-3">
                    <div className={`text-4xl mb-2 ${isEarned ? '' : 'grayscale'}`}>
                      {badge.icon || '🏆'}
                    </div>
                    <h3 className={`font-semibold ${isEarned ? 'text-gray-900' : 'text-gray-500'}`}>
                      {badge.name}
                    </h3>
                  </div>

                  {/* Badge Description */}
                  <p className={`text-sm text-center mb-3 ${
                    isEarned ? 'text-gray-700' : 'text-gray-500'
                  }`}>
                    {badge.description}
                  </p>

                  {/* Badge Requirements */}
                  <div className={`text-xs text-center ${
                    isEarned ? 'text-gray-600' : 'text-gray-400'
                  }`}>
                    {badge.requirements}
                  </div>

                  {/* Earned Date */}
                  {isEarned && userBadge && (
                    <div className="mt-3 pt-3 border-t border-success-200">
                      <div className="text-xs text-success-700 text-center">
                        ✅ Desbloqueado el {new Date(userBadge.earned_at).toLocaleDateString()}
                      </div>
                    </div>
                  )}

                  {/* Lock Overlay for Unearned Badges */}
                  {!isEarned && (
                    <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-50 rounded-xl">
                      <div className="text-3xl text-gray-400">🔒</div>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      ))}

      {/* Empty State */}
      {(!allBadges || allBadges.length === 0) && (
        <div className="card text-center py-12">
          <div className="text-6xl mb-4">🏆</div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            No hay badges disponibles
          </h3>
          <p className="text-gray-600">
            Los badges aparecerán aquí cuando estén configurados en el sistema
          </p>
        </div>
      )}

      {/* Progress Summary */}
      {userBadges && userBadges.length > 0 && (
        <div className="card bg-gradient-to-r from-primary-50 to-success-50">
          <h2 className="text-xl font-semibold mb-4 text-center">
            🎉 ¡Felicitaciones por tus logros!
          </h2>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {userBadges.slice(0, 4).map((userBadge) => (
              <div key={userBadge.id} className="text-center">
                <div className="text-2xl mb-1">{userBadge.badge?.icon || '🏆'}</div>
                <div className="text-sm font-medium">{userBadge.badge?.name}</div>
                <div className="text-xs text-gray-500">
                  {new Date(userBadge.earned_at).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>
          
          {userBadges.length > 4 && (
            <div className="text-center mt-4 text-sm text-gray-600">
              Y {userBadges.length - 4} logros más...
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default Badges
