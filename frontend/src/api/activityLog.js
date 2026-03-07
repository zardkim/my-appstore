import client from './client'

export const activityLogApi = {
  getLogs(params = {}) {
    return client.get('/activity-logs', { params })
  },
  clearOldLogs(daysOlderThan = 30) {
    return client.delete('/activity-logs', { params: { days_older_than: daysOlderThan } })
  }
}
