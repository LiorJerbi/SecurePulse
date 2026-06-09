import axios from 'axios'

const api = axios.create({
    baseURL: 'http://localhost:8000',
    timeout: 30000,
})

export const fetchAlerts = async (severity = null) => {
    const params = severity ? { severity } : {}
    const response = await api.get('/alerts', { params })
    return response.data
}

export const fetchLogs = async (page = 1, pageSize = 20, filters = {}) => {
    const params = { page, page_size: pageSize, ...filters }
    const response = await api.get('/logs', { params })
    return response.data
}

export const analyzeAndFetch = async () => {
    await api.post('/analyze')
    return fetchAlerts()
}

export const explainAlert = async (alertId) => {
    const response = await api.post(`/alerts/${alertId}/explain`)
    return response.data
}

export const fetchHealth = async () => {
    const response = await api.get('/health')
    return response.data
}