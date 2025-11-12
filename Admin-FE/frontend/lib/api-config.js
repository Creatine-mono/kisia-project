/**
 * API 설정 파일
 * 백엔드 호스트 주소를 한 곳에서 관리합니다.
 * 환경 변수 NEXT_PUBLIC_API_URL이 설정되어 있으면 그 값을 사용하고,
 * 없으면 기본값을 사용합니다.
 */

// 환경 변수에서 API URL 가져오기, 없으면 기본값 사용
const getApiUrl = () => {
  // 클라이언트 사이드에서는 process.env.NEXT_PUBLIC_API_URL을 사용
  if (typeof window !== 'undefined') {
    return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  }
  // 서버 사이드
  return process.env.NEXT_PUBLIC_API_URL || process.env.API_URL || 'http://localhost:8000';
};

// API 기본 설정
export const apiConfig = {
  // 백엔드 API 기본 URL
  baseURL: getApiUrl(),
  
  // API 엔드포인트
  endpoints: {
    // 인증 관련
    auth: {
      // OpenAPI 기준 경로로 정정
      login: '/api/v1/auth/login',
      me: '/api/v1/auth/me',
    },
    
    // 로그 관련
    logs: {
      list: '/api/v1/admin/logs',
    },
    
    // 대시보드 관련
    dashboard: {
      overview: '/api/v1/admin/statistics/overview',
      timeline: '/api/v1/admin/statistics/timeline',
      byPiiType: '/api/v1/admin/statistics/by-pii-type',
      byIp: '/api/v1/admin/statistics/by-ip',
    },
    
    // 프로젝트 관련
    // 프로젝트/시스템 설정은 미개발: 추후 연결
    
    // 시스템 설정 관련
    settings: {
      list: '/api/v1/admin/pii-settings',
      detail: (entity) => `/api/v1/admin/pii-settings/${entity}`,
      update: (entity) => `/api/v1/admin/pii-settings/${entity}`,
    },
  },
  
  // API 요청 기본 옵션
  defaultOptions: {
    headers: {
      'Content-Type': 'application/json',
    },
    // credentials 제거: JWT를 localStorage에 저장하므로 쿠키 불필요
    // credentials: 'include',
  },
};

/**
 * 전체 API URL을 생성하는 헬퍼 함수
 * @param {string} endpoint - 엔드포인트 경로
 * @returns {string} 전체 URL
 */
export const getApiEndpoint = (endpoint) => {
  // 이미 전체 URL인 경우 그대로 반환
  if (endpoint.startsWith('http://') || endpoint.startsWith('https://')) {
    return endpoint;
  }
  
  // baseURL에 슬래시가 있고 endpoint도 슬래시로 시작하면 중복 제거
  const baseURL = apiConfig.baseURL.endsWith('/') 
    ? apiConfig.baseURL.slice(0, -1) 
    : apiConfig.baseURL;
  const endpointPath = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  
  return `${baseURL}${endpointPath}`;
};

/**
 * API 요청을 위한 fetch 래퍼 함수
 * @param {string} endpoint - API 엔드포인트
 * @param {RequestInit} options - fetch 옵션
 * @returns {Promise<Response>}
 */
export const apiRequest = async (endpoint, options = {}) => {
  const url = getApiEndpoint(endpoint);
  
  const config = {
    ...apiConfig.defaultOptions,
    ...options,
    headers: {
      ...apiConfig.defaultOptions.headers,
      ...options.headers,
    },
  };
  // Authorization 헤더 자동 주입
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token')
    if (token && !config.headers['Authorization']) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
  }
  
  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      // 401은 별도 에러 코드로 식별
      const err = new Error(`API 요청 실패: ${response.status} ${response.statusText}`)
      err.status = response.status
      throw err
    }
    
    return response;
  } catch (error) {
    console.error('API 요청 오류:', error);
    if (typeof window !== 'undefined' && error?.status === 401) {
      try { localStorage.removeItem('access_token') } catch {}
    }
    throw error;
  }
};

/**
 * JSON 응답을 파싱하는 헬퍼 함수
 * @param {string} endpoint - API 엔드포인트
 * @param {RequestInit} options - fetch 옵션
 * @returns {Promise<any>}
 */
export const apiJson = async (endpoint, options = {}) => {
  const response = await apiRequest(endpoint, options);
  return response.json();
};

// 기본 export
export default apiConfig;

