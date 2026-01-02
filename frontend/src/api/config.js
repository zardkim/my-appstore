import client from './client'

export const configApi = {
  // Get all configuration
  getConfig: () => client.get('/config/'),

  // Get specific section
  getSection: (section) => client.get(`/config/${section}`),

  // Update specific section
  updateSection: (section, data) => client.put(`/config/${section}`, data),

  // Reset to defaults
  reset: () => client.post('/config/reset')
}
