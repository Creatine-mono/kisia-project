import { apiJson, apiConfig } from './api-config'

export const fetchOverview = async ({ start_date, end_date } = {}) => {
	const params = new URLSearchParams()
	if (start_date) params.set('start_date', start_date)
	if (end_date) params.set('end_date', end_date)
	const qs = params.toString() ? `?${params.toString()}` : ''
	return apiJson(`${apiConfig.endpoints.dashboard.overview}${qs}`)
}

export const fetchTimeline = async ({ start_date, end_date, interval } = {}) => {
	const params = new URLSearchParams()
	if (start_date) params.set('start_date', start_date)
	if (end_date) params.set('end_date', end_date)
	if (interval) params.set('interval', interval)
	const qs = params.toString() ? `?${params.toString()}` : ''
	return apiJson(`${apiConfig.endpoints.dashboard.timeline}${qs}`)
}

export const fetchByPiiType = async ({ start_date, end_date } = {}) => {
	const params = new URLSearchParams()
	if (start_date) params.set('start_date', start_date)
	if (end_date) params.set('end_date', end_date)
	const qs = params.toString() ? `?${params.toString()}` : ''
	return apiJson(`${apiConfig.endpoints.dashboard.byPiiType}${qs}`)
}

export const fetchByIp = async ({ start_date, end_date, size } = {}) => {
	const params = new URLSearchParams()
	if (start_date) params.set('start_date', start_date)
	if (end_date) params.set('end_date', end_date)
	if (size) params.set('size', String(size))
	const qs = params.toString() ? `?${params.toString()}` : ''
	return apiJson(`${apiConfig.endpoints.dashboard.byIp}${qs}`)
}

export default {
	fetchOverview,
	fetchTimeline,
	fetchByPiiType,
	fetchByIp,
}
