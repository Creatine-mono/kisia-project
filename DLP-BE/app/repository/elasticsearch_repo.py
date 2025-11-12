"""
Elasticsearch 저장소 레이어
"""
from datetime import datetime, timedelta
from elasticsearch import AsyncElasticsearch, NotFoundError
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class ElasticsearchRepository:
    """Elasticsearch 데이터 접근 레이어"""

    def __init__(self, es_client: AsyncElasticsearch):
        self.client = es_client
        self.index_name = f"{settings.ELASTICSEARCH_INDEX_PREFIX}-logs"

    async def create_index_if_not_exists(self) -> None:
        """
        인덱스가 없으면 생성 (ILM 정책 포함)
        """
        try:
            exists = await self.client.indices.exists(index=self.index_name)
            if not exists:
                # 인덱스 매핑 정의
                mappings = {
                    "properties": {
                        "timestamp": {
                            "type": "date",
                            "format": "strict_date_optional_time||epoch_millis"
                        },
                        "client_ip": {"type": "ip"},
                        "original_text": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        },
                        "text_length": {"type": "integer"},
                        "has_pii": {"type": "boolean"},
                        "detected_entities": {
                            "type": "nested",
                            "properties": {
                                "type": {"type": "keyword"},
                                "value": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {"type": "keyword"}
                                    }
                                },
                                "confidence": {"type": "float"},
                                "token_count": {"type": "integer"}
                            }
                        },
                        "entity_types": {"type": "keyword"},
                        "entity_count": {"type": "integer"},
                        "blocked": {"type": "boolean"},
                        "reason": {"type": "text"},
                        "response_time_ms": {"type": "float"},
                        "model_version": {"type": "keyword"},
                        "api_version": {"type": "keyword"}
                    }
                }

                # ILM 정책 설정 (30일 후 삭제)
                settings_config = {
                    "index": {
                        "lifecycle": {
                            "name": "pii-detection-ilm-policy",
                            "rollover_alias": self.index_name
                        },
                        "number_of_shards": 1,
                        "number_of_replicas": 0
                    }
                }

                await self.client.indices.create(
                    index=self.index_name,
                    mappings=mappings,
                    settings=settings_config
                )
                logger.info(f"Created Elasticsearch index: {self.index_name}")

                # ILM 정책 생성 (아직 없으면)
                await self._create_ilm_policy()

        except Exception as e:
            logger.error(f"Failed to create index: {str(e)}")
            # 인덱스 생성 실패해도 계속 진행 (이미 존재할 수 있음)

    async def _create_ilm_policy(self) -> None:
        """ILM 정책 생성 (30일 후 삭제)"""
        try:
            policy_name = "pii-detection-ilm-policy"
            policy_exists = await self.client.ilm.get_lifecycle(name=policy_name, ignore_unavailable=True)

            if not policy_exists:
                policy = {
                    "policy": {
                        "phases": {
                            "hot": {
                                "actions": {}
                            },
                            "delete": {
                                "min_age": f"{settings.ELASTICSEARCH_LOG_RETENTION_DAYS}d",
                                "actions": {
                                    "delete": {}
                                }
                            }
                        }
                    }
                }
                await self.client.ilm.put_lifecycle(name=policy_name, policy=policy)
                logger.info(f"Created ILM policy: {policy_name}")
        except Exception as e:
            logger.warning(f"Failed to create ILM policy: {str(e)}")

    async def index_log(self, log_data: dict) -> str:
        """
        로그 인덱싱

        Args:
            log_data: 로그 데이터 dict

        Returns:
            str: 생성된 문서 ID
        """
        try:
            # 타임스탬프 추가
            log_data["timestamp"] = datetime.utcnow().isoformat()

            result = await self.client.index(
                index=self.index_name,
                document=log_data,
                refresh="false"  # 비동기 처리 (성능 향상)
            )
            return result["_id"]
        except Exception as e:
            logger.error(f"Failed to index log: {str(e)}")
            raise

    async def search_logs(
        self,
        start_date: datetime,
        end_date: datetime,
        client_ip: str | None = None,
        has_pii: bool | None = None,
        entity_type: str | None = None,
        page: int = 1,
        page_size: int = 20,
        sort: str = "timestamp:desc"
    ) -> dict:
        """
        로그 검색

        Returns:
            dict: {
                "total": int,
                "hits": list[dict]
            }
        """
        try:
            # 쿼리 구성
            must_conditions = [
                {
                    "range": {
                        "timestamp": {
                            "gte": start_date.isoformat(),
                            "lte": end_date.isoformat()
                        }
                    }
                }
            ]

            if client_ip:
                must_conditions.append({"term": {"client_ip": client_ip}})

            if has_pii is not None:
                must_conditions.append({"term": {"has_pii": has_pii}})

            if entity_type:
                must_conditions.append({"term": {"entity_types": entity_type}})

            query = {
                "bool": {
                    "must": must_conditions
                }
            }

            # 정렬 파싱
            sort_field, sort_order = sort.split(":")
            sort_config = [{sort_field: {"order": sort_order}}]

            # 페이징
            from_value = (page - 1) * page_size

            result = await self.client.search(
                index=self.index_name,
                query=query,
                sort=sort_config,
                from_=from_value,
                size=page_size
            )

            return {
                "total": result["hits"]["total"]["value"],
                "hits": [hit["_source"] | {"id": hit["_id"]} for hit in result["hits"]["hits"]]
            }

        except NotFoundError:
            # 인덱스가 아직 없으면 빈 결과 반환
            return {"total": 0, "hits": []}
        except Exception as e:
            logger.error(f"Failed to search logs: {str(e)}")
            raise

    async def aggregate_statistics(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> dict:
        """
        전체 통계 집계

        Returns:
            dict: 집계 결과
        """
        try:
            query = {
                "range": {
                    "timestamp": {
                        "gte": start_date.isoformat(),
                        "lte": end_date.isoformat()
                    }
                }
            }

            aggs = {
                "total_requests": {"value_count": {"field": "timestamp"}},
                "detected_requests": {
                    "filter": {"term": {"has_pii": True}}
                },
                "unique_ips": {
                    "cardinality": {"field": "client_ip"}
                },
                "avg_response_time": {
                    "avg": {"field": "response_time_ms"}
                },
                "top_pii_types": {
                    "terms": {
                        "field": "entity_types",
                        "size": 10
                    },
                    "aggs": {
                        "avg_confidence": {
                            "avg": {
                                "script": {
                                    "source": """
                                        double sum = 0;
                                        int count = 0;
                                        for (entity in params._source.detected_entities) {
                                            if (entity.type == params.pii_type) {
                                                sum += entity.confidence;
                                                count++;
                                            }
                                        }
                                        return count > 0 ? sum / count : 0;
                                    """,
                                    "params": {"pii_type": "dummy"}
                                }
                            }
                        }
                    }
                },
                "top_ips": {
                    "terms": {
                        "field": "client_ip",
                        "size": 10
                    },
                    "aggs": {
                        "detected_count": {
                            "filter": {"term": {"has_pii": True}}
                        }
                    }
                }
            }

            result = await self.client.search(
                index=self.index_name,
                query=query,
                aggs=aggs,
                size=0  # 문서 결과는 필요 없음
            )

            return result["aggregations"]

        except NotFoundError:
            # 인덱스가 없으면 빈 통계 반환
            return {}
        except Exception as e:
            logger.error(f"Failed to aggregate statistics: {str(e)}")
            raise

    async def aggregate_timeline(
        self,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1h"
    ) -> dict:
        """
        시간대별 추세 집계

        Args:
            interval: "1h", "1d", "1w" 등
        """
        try:
            query = {
                "range": {
                    "timestamp": {
                        "gte": start_date.isoformat(),
                        "lte": end_date.isoformat()
                    }
                }
            }

            aggs = {
                "timeline": {
                    "date_histogram": {
                        "field": "timestamp",
                        "calendar_interval": interval,
                        "format": "yyyy-MM-dd'T'HH:mm:ss'Z'"
                    },
                    "aggs": {
                        "detected_count": {
                            "filter": {"term": {"has_pii": True}}
                        }
                    }
                }
            }

            result = await self.client.search(
                index=self.index_name,
                query=query,
                aggs=aggs,
                size=0
            )

            return result["aggregations"]["timeline"]["buckets"]

        except NotFoundError:
            return []
        except Exception as e:
            logger.error(f"Failed to aggregate timeline: {str(e)}")
            raise

    async def aggregate_by_ip(
        self,
        start_date: datetime,
        end_date: datetime,
        size: int = 20
    ) -> dict:
        """
        IP별 통계 집계
        """
        try:
            query = {
                "range": {
                    "timestamp": {
                        "gte": start_date.isoformat(),
                        "lte": end_date.isoformat()
                    }
                }
            }

            aggs = {
                "by_ip": {
                    "terms": {
                        "field": "client_ip",
                        "size": size
                    },
                    "aggs": {
                        "detected_count": {
                            "filter": {"term": {"has_pii": True}}
                        },
                        "top_pii_type": {
                            "terms": {
                                "field": "entity_types",
                                "size": 1
                            }
                        }
                    }
                }
            }

            result = await self.client.search(
                index=self.index_name,
                query=query,
                aggs=aggs,
                size=0
            )

            return result["aggregations"]["by_ip"]["buckets"]

        except NotFoundError:
            return []
        except Exception as e:
            logger.error(f"Failed to aggregate by IP: {str(e)}")
            raise