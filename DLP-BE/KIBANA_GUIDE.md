# Kibana 대시보드 설정 가이드

PII 검사 로그를 Kibana에서 시각화하고 모니터링하는 방법입니다.

---

## 📋 목차

1. [사전 준비](#사전-준비)
2. [Index Pattern 생성](#index-pattern-생성)
3. [Discover에서 로그 확인](#discover에서-로그-확인)
4. [Visualize로 차트 만들기](#visualize로-차트-만들기)
5. [Dashboard 구성](#dashboard-구성)
6. [추가 팁](#추가-팁)

---

## 사전 준비

### 1. Elasticsearch & Kibana 시작

```bash
# Docker Compose로 실행
cd /Users/sun/개발/KISIA/project/DLP-BE
docker-compose up -d

# 상태 확인
docker-compose ps
```

### 2. Kibana 접속

브라우저에서 http://localhost:5601 접속

### 3. 테스트 데이터 생성

백엔드 서버를 실행하고 PII 검사 요청을 몇 개 보냅니다:

```bash
# 서버 실행 (다른 터미널)
uv run uvicorn app.main:app --reload --port 8000

# 테스트 요청 (또 다른 터미널)
curl -X POST "http://localhost:8000/api/v1/pii/detect" \
  -H "Content-Type: application/json" \
  -d '{"text": "제 이름은 홍길동이고 전화번호는 010-1234-5678입니다"}'

curl -X POST "http://localhost:8000/api/v1/pii/detect" \
  -H "Content-Type: application/json" \
  -d '{"text": "오늘 날씨가 좋습니다"}'

curl -X POST "http://localhost:8000/api/v1/pii/detect" \
  -H "Content-Type: application/json" \
  -d '{"text": "김철수의 이메일은 test@example.com입니다"}' \
  -H "X-Forwarded-For: 192.168.1.100"
```

**중요**: 로그가 Elasticsearch에 저장되기까지 1-2초 정도 소요됩니다.

---

## Index Pattern 생성

### 1. Management 메뉴 접속

Kibana 좌측 메뉴 → **Management** → **Stack Management** 클릭

### 2. Index Patterns 생성

1. 좌측 메뉴에서 **Data Views** (또는 **Index Patterns**) 클릭
2. **Create data view** 버튼 클릭
3. 설정 입력:
   - **Name**: `PII Detection Logs`
   - **Index pattern**: `pii-detection-logs`
   - **Timestamp field**: `timestamp` 선택
4. **Save data view to Kibana** 버튼 클릭

✅ 완료! 이제 `pii-detection-logs` 인덱스의 데이터를 Kibana에서 볼 수 있습니다.

---

## Discover에서 로그 확인

### 1. Discover 메뉴 접속

좌측 메뉴 → **Discover** 클릭

### 2. 시간 범위 설정

우측 상단의 시간 선택기 클릭 → **Last 15 minutes** 또는 **Last 1 hour** 선택

### 3. 필드 확인

좌측 **Available fields**에서 다음 필드들을 확인:

- `timestamp` - 요청 시간
- `client_ip` - 클라이언트 IP
- `has_pii` - PII 탐지 여부
- `original_text` - 원문 텍스트
- `entity_types` - 탐지된 PII 타입
- `entity_count` - 탐지된 개수
- `response_time_ms` - 응답 시간

### 4. 필드 추가하기

원하는 필드를 테이블에 추가:

1. 필드명 위에 마우스 오버
2. **+** 버튼 클릭

추천 필드:
- `timestamp`
- `client_ip`
- `has_pii`
- `entity_types`
- `entity_count`
- `response_time_ms`

### 5. 필터링

**PII 탐지된 로그만 보기:**

1. 검색창에 입력: `has_pii: true`
2. Enter 키

**특정 IP 로그만 보기:**

```
client_ip: "192.168.1.100"
```

**특정 PII 타입 검색:**

```
entity_types: "PERSON"
```

---

## Visualize로 차트 만들기

### 1. Visualize Library 접속

좌측 메뉴 → **Visualize Library** 클릭 → **Create visualization** 버튼

### 차트 1: PII 탐지율 (Pie Chart)

**목적**: PII 탐지/미탐지 비율 시각화

1. **Pie** 차트 선택
2. Data view: `PII Detection Logs` 선택
3. 설정:
   - **Slice by**: `Terms` 선택
     - Field: `has_pii`
     - Size: 10
   - **Metrics**: Count
4. 우측 상단 **Save** → 이름: `PII Detection Rate`

### 차트 2: 시간대별 요청량 (Line Chart)

**목적**: 시간에 따른 요청 추세 확인

1. **Line** 차트 선택
2. Data view: `PII Detection Logs` 선택
3. 설정:
   - **Horizontal axis**:
     - Aggregation: `Date Histogram`
     - Field: `timestamp`
     - Minimum interval: `Auto`
   - **Vertical axis**:
     - Aggregation: `Count`
   - **Break down by**: (선택사항)
     - Terms: `has_pii`
4. **Save** → 이름: `Requests Over Time`

### 차트 3: PII 타입별 분포 (Bar Chart)

**목적**: 어떤 PII 타입이 가장 많이 탐지되는지 확인

1. **Bar Vertical** 차트 선택
2. Data view: `PII Detection Logs` 선택
3. 설정:
   - **Horizontal axis**:
     - Aggregation: `Terms`
     - Field: `entity_types`
     - Size: 10
     - Order by: `Metric: Count`
     - Order: `Descending`
   - **Vertical axis**:
     - Aggregation: `Count`
4. **Save** → 이름: `Top PII Types`

### 차트 4: Top IP 주소 (Data Table)

**목적**: 가장 많이 요청하는 IP 확인

1. **Table** 선택
2. Data view: `PII Detection Logs` 선택
3. 설정:
   - **Rows**:
     - Aggregation: `Terms`
     - Field: `client_ip`
     - Size: 10
   - **Metrics**:
     - Metric 1: `Count` (총 요청 수)
     - Metric 2 추가:
       - Aggregation: `Filtered metric`
       - Filter: `has_pii: true`
       - Metric: `Count`
4. **Save** → 이름: `Top IP Addresses`

### 차트 5: 응답 시간 분포 (Metric)

**목적**: 평균 응답 시간 모니터링

1. **Metric** 선택
2. Data view: `PII Detection Logs` 선택
3. 설정:
   - **Metric**:
     - Aggregation: `Average`
     - Field: `response_time_ms`
   - **Options**:
     - Suffix: ` ms`
4. **Save** → 이름: `Average Response Time`

### 차트 6: IP별 히트맵 (Heat Map)

**목적**: IP와 시간대별 요청 패턴 시각화

1. **Heat map** 선택
2. Data view: `PII Detection Logs` 선택
3. 설정:
   - **Y-axis**:
     - Aggregation: `Terms`
     - Field: `client_ip`
     - Size: 20
   - **X-axis**:
     - Aggregation: `Date Histogram`
     - Field: `timestamp`
     - Minimum interval: `1h`
   - **Value**:
     - Aggregation: `Count`
4. **Save** → 이름: `IP Activity Heatmap`

---

## Dashboard 구성

### 1. Dashboard 생성

1. 좌측 메뉴 → **Dashboard** 클릭
2. **Create dashboard** 버튼 클릭

### 2. 차트 추가

1. 우측 상단 **Add** 버튼 클릭
2. 이전에 만든 차트들 선택:
   - `PII Detection Rate` (좌측 상단)
   - `Average Response Time` (우측 상단)
   - `Requests Over Time` (중앙 상단, 넓게)
   - `Top PII Types` (중앙 좌측)
   - `Top IP Addresses` (중앙 우측)
   - `IP Activity Heatmap` (하단, 넓게)

### 3. 차트 배치

드래그 앤 드롭으로 차트 크기와 위치 조정

**추천 레이아웃:**

```
┌─────────────────────────────────────────────────┐
│  PII Detection    │   Avg Response   │          │
│      Rate         │      Time        │          │
├─────────────────────────────────────────────────┤
│                                                  │
│           Requests Over Time (Line)              │
│                                                  │
├────────────────────┬────────────────────────────┤
│                    │                             │
│   Top PII Types    │   Top IP Addresses          │
│     (Bar)          │       (Table)               │
│                    │                             │
├─────────────────────────────────────────────────┤
│                                                  │
│         IP Activity Heatmap                      │
│                                                  │
└─────────────────────────────────────────────────┘
```

### 4. 대시보드 저장

1. 우측 상단 **Save** 버튼 클릭
2. Title: `PII Detection Monitoring`
3. Description: `PII 검사 실시간 모니터링 대시보드`
4. **Save** 클릭

### 5. 시간 범위 설정

우측 상단 시간 선택기 → **Last 24 hours** 선택

### 6. 자동 새로고침 설정

우측 상단 시계 아이콘 → **Auto-refresh** → **10 seconds** 선택

---

## 추가 팁

### 💡 실시간 모니터링

1. Dashboard 화면에서 우측 상단 **Share** → **Copy link**
2. 링크를 북마크하거나 모니터링 화면에 띄워놓기
3. Auto-refresh를 활성화하여 실시간 업데이트

### 💡 알림 설정 (Kibana Alerting)

**조건**: 5분 동안 PII 탐지가 100건 이상

1. 좌측 메뉴 → **Stack Management** → **Rules and Connectors**
2. **Create rule** 클릭
3. Rule type: **Elasticsearch query**
4. 설정:
   - Index: `pii-detection-logs`
   - Query: `has_pii: true`
   - Threshold: `IS ABOVE 100`
   - Time window: `5 minutes`
5. Actions: 이메일/슬랙 등 연동 가능

### 💡 커스텀 쿼리 예시

**최근 1시간 동안 PII 탐지된 고유 IP 수:**

```
GET /pii-detection-logs/_search
{
  "query": {
    "bool": {
      "must": [
        {"term": {"has_pii": true}},
        {"range": {"timestamp": {"gte": "now-1h"}}}
      ]
    }
  },
  "aggs": {
    "unique_ips": {
      "cardinality": {"field": "client_ip"}
    }
  },
  "size": 0
}
```

**특정 IP의 최근 요청 10개:**

```
GET /pii-detection-logs/_search
{
  "query": {
    "term": {"client_ip": "192.168.1.100"}
  },
  "sort": [{"timestamp": "desc"}],
  "size": 10
}
```

### 💡 인덱스 관리

**인덱스 삭제 (주의!):**

```bash
curl -X DELETE "http://localhost:9200/pii-detection-logs"
```

**인덱스 통계 확인:**

```bash
curl "http://localhost:9200/pii-detection-logs/_stats?pretty"
```

### 💡 성능 최적화

1. **인덱스 강제 새로고침** (테스트용):
   ```bash
   curl -X POST "http://localhost:9200/pii-detection-logs/_refresh"
   ```

2. **오래된 데이터 정리** (ILM 정책이 자동으로 처리):
   - 30일 후 자동 삭제
   - 수동 삭제는 권장하지 않음

---

## 📊 완성된 대시보드 예시

완성 후 다음과 같은 인사이트를 얻을 수 있습니다:

✅ **실시간 모니터링**:
- 현재 PII 탐지율
- 평균 응답 시간
- 시간대별 트래픽 추세

✅ **패턴 분석**:
- 가장 많이 탐지되는 PII 타입
- 특정 IP의 비정상적 활동
- 피크 타임 파악

✅ **보안 모니터링**:
- 의심스러운 IP 추적
- 대량 PII 탐지 감지
- 응답 시간 급증 알림

---

## 🔧 문제 해결

### 로그가 보이지 않을 때

1. **Elasticsearch 연결 확인**:
   ```bash
   curl http://localhost:9200/_cluster/health?pretty
   ```

2. **인덱스 확인**:
   ```bash
   curl http://localhost:9200/_cat/indices?v | grep pii-detection
   ```

3. **최근 로그 수동 조회**:
   ```bash
   curl http://localhost:9200/pii-detection-logs/_search?pretty
   ```

4. **시간 범위 확장**: Kibana에서 시간 범위를 **Last 7 days**로 변경

### 차트가 제대로 표시되지 않을 때

1. **필드 매핑 확인**:
   - Management → Index Patterns → `pii-detection-logs` → Refresh field list

2. **데이터 타입 확인**:
   - 숫자 필드가 `text`로 인식되는 경우 재인덱싱 필요

3. **시간 동기화**:
   - 서버 시간과 Kibana 시간이 일치하는지 확인

---

## 🎓 다음 단계

1. **알림 시스템 구축**: Kibana Alerting 또는 ElastAlert 사용
2. **Machine Learning**: Kibana ML로 이상 탐지
3. **보고서 자동화**: Kibana Reporting으로 일일 리포트
4. **커스텀 대시보드**: 비즈니스 요구사항에 맞춰 추가 차트 생성

---

**문서 작성일**: 2025-10-29
**버전**: 1.0