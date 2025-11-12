import { apiJson, apiRequest, apiConfig } from './api-config'

export const fetchAllSettings = async () => {
	try {
		console.log('fetchAllSettings 호출')
		console.log('API URL:', apiConfig.endpoints.settings.list)
		const result = await apiJson(apiConfig.endpoints.settings.list)
		console.log('fetchAllSettings 응답:', result)
		return result
	} catch (error) {
		console.error('fetchAllSettings 에러:', error)
		throw error
	}
}

export const fetchSetting = async (entityType) => {
	try {
		const result = await apiJson(apiConfig.endpoints.settings.detail(entityType))
		console.log(`fetchSetting(${entityType}) 응답:`, result)
		return result
	} catch (error) {
		console.error(`fetchSetting(${entityType}) 에러:`, error)
		throw error
	}
}

export const updateSetting = async (entityType, { enabled, threshold } = {}) => {
	try {
		const body = {}
		if (typeof enabled === 'boolean') body.enabled = enabled
		if (typeof threshold === 'number') body.threshold = threshold

		console.log(`updateSetting(${entityType}) 요청:`, body)

		const res = await apiRequest(apiConfig.endpoints.settings.update(entityType), {
			method: 'PATCH',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(body),
		})

		const result = await res.json()
		console.log(`updateSetting(${entityType}) 응답:`, result)
		return result
	} catch (error) {
		console.error(`updateSetting(${entityType}) 에러:`, error)
		throw error
	}
}

export default {
	fetchAllSettings,
	fetchSetting,
	updateSetting,
}
