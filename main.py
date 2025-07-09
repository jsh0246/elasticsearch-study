from elasticsearch import Elasticsearch
import traceback
import json

# Elasticsearch 연결 설정
es = Elasticsearch(
    "http://localhost:9200",
    basic_auth=("elastic", "OBIpKj46")
)

def print_section(title):
    print("\n" + "="*50)
    print(f"📚 {title}")
    print("="*50)

def main():
    try:
        # 1. 연결 확인
        print_section("1. Elasticsearch 연결 확인")
        if es.ping():
            print("✅ Elasticsearch 연결 성공")
            info = es.info()
            print(f"클러스터 이름: {info['cluster_name']}")
            print(f"버전: {info['version']['number']}")
        else:
            print("❌ Elasticsearch 연결 실패")
            return

        # 2. 인덱스 생성
        print_section("2. 인덱스 생성")
        index_name = "books"
        
        # 인덱스가 이미 존재하는지 확인
        if es.indices.exists(index=index_name):
            print(f"📝 인덱스 '{index_name}'이(가) 이미 존재합니다. 삭제 후 재생성...")
            es.indices.delete(index=index_name)
        
        # 인덱스 생성 (매핑 설정)
        mapping = {
            "mappings": {
                "properties": {
                    "title": {
                        "type": "text",
                        "analyzer": "standard"
                    },
                    "author": {
                        "type": "keyword"
                    },
                    "publish_date": {
                        "type": "date"
                    },
                    "price": {
                        "type": "float"
                    },
                    "pages": {
                        "type": "integer"
                    },
                    "description": {
                        "type": "text"
                    }
                }
            }
        }
        
        es.indices.create(index=index_name, body=mapping)
        print(f"✅ 인덱스 '{index_name}' 생성 완료")

        # 3. 문서 추가 (Indexing)
        print_section("3. 문서 추가")
        documents = [
            {
                "title": "Python으로 배우는 머신러닝",
                "author": "김철수",
                "publish_date": "2023-01-15",
                "price": 25000,
                "pages": 450,
                "description": "Python을 사용한 머신러닝 입문서"
            },
            {
                "title": "Django 웹 개발",
                "author": "이영희",
                "publish_date": "2023-03-20",
                "price": 30000,
                "pages": 600,
                "description": "Django를 이용한 웹 애플리케이션 개발"
            },
            {
                "title": "Elasticsearch 완벽 가이드",
                "author": "박민수",
                "publish_date": "2023-05-10",
                "price": 35000,
                "pages": 800,
                "description": "Elasticsearch 검색 엔진의 모든 것"
            }
        ]
        
        for i, doc in enumerate(documents, 1):
            es.index(index=index_name, id=i, body=doc)
            print(f"📄 문서 {i} 추가: {doc['title']}")
        
        # 인덱스 새로고침 (검색 가능하도록)
        es.indices.refresh(index=index_name)
        print("🔄 인덱스 새로고침 완료")

        # 4. 문서 조회
        print_section("4. 문서 조회")
        doc = es.get(index=index_name, id=1)
        print("📖 ID 1번 문서:")
        print(json.dumps(doc['_source'], indent=2, ensure_ascii=False))

        # 5. 전체 문서 검색
        print_section("5. 전체 문서 검색")
        query = {
            "query": {
                "match_all": {}
            }
        }
        
        result = es.search(index=index_name, body=query)
        print(f"📊 총 {result['hits']['total']['value']}개 문서 발견:")
        for hit in result['hits']['hits']:
            print(f"  - {hit['_source']['title']} (작가: {hit['_source']['author']})")

        # 6. 키워드 검색
        print_section("6. 키워드 검색")
        query = {
            "query": {
                "match": {
                    "title": "Python"
                }
            }
        }
        
        result = es.search(index=index_name, body=query)
        print(f"🔍 'Python' 키워드 검색 결과: {result['hits']['total']['value']}개")
        for hit in result['hits']['hits']:
            print(f"  - {hit['_source']['title']} (점수: {hit['_score']})")

        # 7. 범위 검색
        print_section("7. 범위 검색")
        query = {
            "query": {
                "range": {
                    "price": {
                        "gte": 25000,
                        "lte": 30000
                    }
                }
            }
        }
        
        result = es.search(index=index_name, body=query)
        print(f"💰 가격 25,000~30,000원 범위 검색 결과: {result['hits']['total']['value']}개")
        for hit in result['hits']['hits']:
            print(f"  - {hit['_source']['title']} (가격: {hit['_source']['price']:,}원)")

        # 8. 집계 (Aggregations)
        print_section("8. 집계 분석")
        agg_query = {
            "size": 0,
            "aggs": {
                "avg_price": {
                    "avg": {
                        "field": "price"
                    }
                },
                "max_pages": {
                    "max": {
                        "field": "pages"
                    }
                },
                "authors": {
                    "terms": {
                        "field": "author"
                    }
                }
            }
        }
        
        result = es.search(index=index_name, body=agg_query)
        aggregations = result['aggregations']
        
        print(f"📈 평균 가격: {aggregations['avg_price']['value']:,.0f}원")
        print(f"📖 최대 페이지: {aggregations['max_pages']['value']}페이지")
        print("👥 작가별 문서 수:")
        for bucket in aggregations['authors']['buckets']:
            print(f"  - {bucket['key']}: {bucket['doc_count']}권")

        # 9. 문서 업데이트
        print_section("9. 문서 업데이트")
        update_doc = {
            "doc": {
                "price": 27000,
                "description": "Python을 사용한 머신러닝 입문서 (개정판)"
            }
        }
        
        es.update(index=index_name, id=1, body=update_doc)
        print("📝 ID 1번 문서 업데이트 완료")
        
        # 업데이트된 문서 확인
        updated_doc = es.get(index=index_name, id=1)
        print(f"💰 업데이트된 가격: {updated_doc['_source']['price']:,}원")

        # 10. 복합 쿼리
        print_section("10. 복합 쿼리")
        complex_query = {
            "query": {
                "bool": {
                    "must": [
                        {"match": {"description": "Python"}}
                    ],
                    "filter": [
                        {"range": {"price": {"gte": 25000}}}
                    ]
                }
            }
        }
        
        result = es.search(index=index_name, body=complex_query)
        print(f"🔍 복합 쿼리 결과: {result['hits']['total']['value']}개")
        for hit in result['hits']['hits']:
            print(f"  - {hit['_source']['title']} (가격: {hit['_source']['price']:,}원)")

        print_section("✅ 모든 실습 완료!")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        print("상세 오류 정보:")
        traceback.print_exc()

if __name__ == "__main__":
    main()