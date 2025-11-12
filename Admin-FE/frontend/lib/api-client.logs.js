import { apiJson, apiConfig } from './api-config'

export const fetchLogs = async ({
	start_date,
	end_date,
	client_ip,
	has_pii,
	entity_type,
	page = 1,
	page_size = 20,
	sort = 'timestamp:desc',
} = {}) => {
	const params = new URLSearchParams()
	if (start_date) params.set('start_date', start_date)
	if (end_date) params.set('end_date', end_date)
	if (client_ip) params.set('client_ip', client_ip)
	if (typeof has_pii === 'boolean') params.set('has_pii', String(has_pii))
	if (entity_type) params.set('entity_type', entity_type)
	if (page) params.set('page', String(page))
	if (page_size) params.set('page_size', String(page_size))
	if (sort) params.set('sort', sort)
	const qs = params.toString() ? `?${params.toString()}` : ''
	return apiJson(`${apiConfig.endpoints.logs.list}${qs}`)
}

export default {
	fetchLogs,
}
