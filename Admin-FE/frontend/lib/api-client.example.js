/**
 * API 클라이언트 사용 예시
 * 
 * 이 파일은 api-config.js를 사용하는 방법을 보여주는 예시입니다.
 * 실제 프로젝트에서는 이 패턴을 따라 API 호출을 구현하세요.
 */

import { apiConfig, apiJson, apiRequest, getApiEndpoint } from './api-config';

// 예시 1: 간단한 GET 요청
export const fetchLogs = async () => {
  try {
    const logs = await apiJson(apiConfig.endpoints.logs.list);
    return logs;
  } catch (error) {
    console.error('로그 조회 실패:', error);
    throw error;
  }
};

// 예시 2: POST 요청
export const login = async (email, password) => {
  try {
    const response = await apiRequest(apiConfig.endpoints.auth.login, {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    return response.json();
  } catch (error) {
    console.error('로그인 실패:', error);
    throw error;
  }
};

// 예시 3: 동적 엔드포인트 사용
export const getLogDetail = async (logId) => {
  try {
    const log = await apiJson(apiConfig.endpoints.logs.detail(logId));
    return log;
  } catch (error) {
    console.error('로그 상세 조회 실패:', error);
    throw error;
  }
};

// 예시 4: 커스텀 헤더가 필요한 경우
export const updateProject = async (projectId, data) => {
  try {
    const token = localStorage.getItem('authToken'); // 예시
    
    const response = await apiRequest(
      apiConfig.endpoints.projects.update(projectId),
      {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      }
    );
    return response.json();
  } catch (error) {
    console.error('프로젝트 업데이트 실패:', error);
    throw error;
  }
};

// 예시 5: 직접 URL 구성
export const customApiCall = async () => {
  const url = getApiEndpoint('/api/custom/endpoint');
  // fetch 또는 apiRequest 사용
  return apiJson(url);
};

// 예시 6: 대시보드 통계 조회
export const fetchDashboardStats = async () => {
  try {
    const stats = await apiJson(apiConfig.endpoints.dashboard.stats);
    return stats;
  } catch (error) {
    console.error('대시보드 통계 조회 실패:', error);
    throw error;
  }
};

// 사용 예시 (컴포넌트에서):
/*
"use client"

import { useEffect, useState } from 'react';
import { fetchLogs } from '@/lib/api-client.example';

export default function LogsPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadLogs = async () => {
      try {
        const data = await fetchLogs();
        setLogs(data);
      } catch (error) {
        console.error('로그 로드 실패:', error);
      } finally {
        setLoading(false);
      }
    };
    
    loadLogs();
  }, []);

  if (loading) return <div>로딩 중...</div>;

  return (
    <div>
      {logs.map(log => (
        <div key={log.id}>{log.event}</div>
      ))}
    </div>
  );
}
*/

