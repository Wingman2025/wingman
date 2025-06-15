import axios from 'axios'

// Get API base URL from environment
const getApiBaseUrl = () => {
  // In production, use the Railway backend URL directly
  if (import.meta.env.PROD) {
    return import.meta.env.VITE_API_BASE_URL || 'https://wingman-dev.up.railway.app'
  }
  // In development, use proxy
  return '/api'
}

// Create axios instance with base configuration
const api = axios.create({
  baseURL: getApiBaseUrl(),
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important for Flask session cookies
})

// Request interceptor to handle authentication
api.interceptors.request.use(
  (config) => {
    // In production, we need to handle CORS and authentication differently
    if (import.meta.env.PROD) {
      // Add /api prefix for production calls
      if (!config.url.startsWith('/api')) {
        config.url = `/api${config.url}`
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      console.warn('Usuario no autenticado')
    }
    return Promise.reject(error)
  }
)

// Goals API
export const goalsApi = {
  getUserGoals: () => api.get('/user_goals'),
  createGoal: (goalData) => api.post('/create_goal', goalData),
  updateGoalProgress: (goalId, progress) => 
    api.patch(`/update_goal_progress`, { goal_id: goalId, progress }),
  getGoalTemplates: () => api.get('/goal_templates'),
}

// Badges API
export const badgesApi = {
  getUserBadges: () => api.get('/user_badges'),
  getAllBadges: () => api.get('/badges'),
  unlockBadge: (badgeId) => api.post('/unlock_badge', { badge_id: badgeId }),
}

// Stats API
export const statsApi = {
  getMotivationalStats: () => api.get('/motivational_stats'),
}

export default api
