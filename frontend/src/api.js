const request = async (url, options = {}) => {
  const resp = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    ...options
  })
  if (!resp.ok) {
    const error = await resp.json().catch(() => ({ message: 'Request failed' }))
    throw new Error(error.message || 'Request failed')
  }
  return resp.json()
}

export const api = {
  getUser: (id) => request(`/api/users/${id}`),
  getTasks: (userId) => request(`/api/tasks?user_id=${userId}`),
  completeTask: (taskId) => request(`/api/tasks/${taskId}/complete`, { method: 'POST', body: JSON.stringify({ reviewer_passed: true }) }),
  getTeam: (teamId) => request(`/api/teams/${teamId}`),
  getRewards: () => request('/api/rewards'),
  redeem: (userId, rewardId) => request('/api/rewards/redeem', { method: 'POST', body: JSON.stringify({ user_id: userId, reward_id: rewardId }) })
}
