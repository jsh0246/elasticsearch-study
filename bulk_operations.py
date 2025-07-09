from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import json
import random
from datetime import datetime, timedelta

# Elasticsearch 연결 설정
es = Elasticsearch(
    "http://localhost:9200",
    basic_auth=("elastic", "OBIpKj46")
)

def print_section(title):
    print("\n" + "="*50)
    print(f"📦 {title}")
    print("="*50)

def generate_sample_data(count=100):
    """샘플 데이터 생성"""
    categories = ['프로그래밍', '데이터사이언스', '웹개발', '머신러닝', '인공지능', '클라우드', '보안', '모바일']
    authors = ['김철수', '이영희', '박민수', '최지은', '정동훈', '홍길동', '김영수', '이민정']
    
    languages = ['Python', 'Java', 'JavaScript', 'C++', 'Go', 'Rust', 'TypeScript', 'Kotlin']
    adjectives = ['완벽한', '실용적인', '전문가를 위한', '초보자를 위한', '고급', '기초', '심화']
    
    data = []
    
    for i in range(count):
        # 랜덤 데이터 생성
        category = random.choice(categories)
        author = random.choice(authors)
        language = random.choice(languages)
        adjective = random.choice(adjectives)
        
        # 날짜 범위 (최근 2년)
        start_date = datetime.now() - timedelta(days=730)
        random_days = random.randint(0, 730)
        pub_date = start_date + timedelta(days=random_days)
        
        doc = {
            "title": f"{adjective} {language} {category}",
            "author": author,
            "category": category,
            "language": language,
            "publish_date": pub_date.strftime("%Y-%m-%d"),
            "price": random.randint(15000, 50000),
            "pages": random.randint(200, 800),
            "rating": round(random.uniform(3.0, 5.0), 1),
            "description": f"{language}를 사용한 {category} 전문서적. {adjective} 접근 방식으로 실무에 바로 적용할 수 있습니다.",
            "tags": [language.lower(), category, "programming"] + random.sample(['tutorial', 'advanced', 'beginner', 'expert'], 2)
        }
        
        data.append(doc)
    
    return data

def main():
    print_section("벌크 인덱싱 실습")
    
    index_name = "tech_books"
    
    # 1. 인덱스 삭제 및 재생성
    print("🗑️ 기존 인덱스 삭제...")
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
        print(f"   '{index_name}' 인덱스 삭제 완료")
    
    # 2. 새로운 인덱스 생성 (한국어 검색 최적화)
    print("🏗️ 새로운 인덱스 생성...")
    
    index_settings = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "analysis": {
                "analyzer": {
                    "korean_analyzer": {
                        "type": "standard",
                        "stopwords": "_none_"
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "title": {
                    "type": "text",
                    "analyzer": "korean_analyzer"
                },
                "author": {"type": "keyword"},
                "category": {"type": "keyword"},
                "language": {"type": "keyword"},
                "publish_date": {"type": "date"},
                "price": {"type": "integer"},
                "pages": {"type": "integer"},
                "rating": {"type": "float"},
                "description": {
                    "type": "text",
                    "analyzer": "korean_analyzer"
                },
                "tags": {"type": "keyword"}
            }
        }
    }
    
    es.indices.create(index=index_name, body=index_settings)
    print(f"   '{index_name}' 인덱스 생성 완료")
    
    # 3. 벌크 데이터 생성
    print("📝 샘플 데이터 생성...")
    sample_data = generate_sample_data(100)
    print(f"   {len(sample_data)}개의 샘플 문서 생성 완료")
    
    # 4. 벌크 인덱싱
    print("📦 벌크 인덱싱 시작...")
    
    def doc_generator():
        for i, doc in enumerate(sample_data):
            yield {
                "_index": index_name,
                "_id": i + 1,
                "_source": doc
            }
    
    # 벌크 인덱싱 실행
    success_count, failed_docs = bulk(es, doc_generator(), chunk_size=50)
    print(f"   성공: {success_count}개, 실패: {len(failed_docs)}개")
    
    # 5. 인덱스 새로고침
    es.indices.refresh(index=index_name)
    print("🔄 인덱스 새로고침 완료")
    
    # 6. 인덱싱 결과 확인
    print_section("인덱싱 결과 확인")
    
    total_count = es.count(index=index_name)
    print(f"📊 총 문서 수: {total_count['count']}개")
    
    # 7. 카테고리별 집계
    print_section("카테고리별 집계")
    
    category_agg = {
        "size": 0,
        "aggs": {
            "categories": {
                "terms": {
                    "field": "category",
                    "size": 10
                }
            },
            "languages": {
                "terms": {
                    "field": "language",
                    "size": 10
                }
            },
            "price_stats": {
                "stats": {
                    "field": "price"
                }
            }
        }
    }
    
    agg_result = es.search(index=index_name, body=category_agg)
    
    print("📈 카테고리별 분포:")
    for bucket in agg_result['aggregations']['categories']['buckets']:
        print(f"   {bucket['key']}: {bucket['doc_count']}권")
    
    print("\n💻 언어별 분포:")
    for bucket in agg_result['aggregations']['languages']['buckets']:
        print(f"   {bucket['key']}: {bucket['doc_count']}권")
    
    price_stats = agg_result['aggregations']['price_stats']
    print(f"\n💰 가격 통계:")
    print(f"   평균: {price_stats['avg']:,.0f}원")
    print(f"   최소: {price_stats['min']:,.0f}원")
    print(f"   최대: {price_stats['max']:,.0f}원")
    
    # 8. 복합 검색 테스트
    print_section("복합 검색 테스트")
    
    complex_queries = [
        {
            "name": "Python 관련 고가 도서",
            "query": {
                "bool": {
                    "must": [
                        {"match": {"language": "Python"}}
                    ],
                    "filter": [
                        {"range": {"price": {"gte": 35000}}}
                    ]
                }
            }
        },
        {
            "name": "평점 4.5 이상 웹개발 도서",
            "query": {
                "bool": {
                    "must": [
                        {"match": {"category": "웹개발"}}
                    ],
                    "filter": [
                        {"range": {"rating": {"gte": 4.5}}}
                    ]
                }
            }
        },
        {
            "name": "최근 1년간 출간된 머신러닝 도서",
            "query": {
                "bool": {
                    "must": [
                        {"match": {"category": "머신러닝"}}
                    ],
                    "filter": [
                        {"range": {"publish_date": {"gte": "2023-01-01"}}}
                    ]
                }
            }
        }
    ]
    
    for query_info in complex_queries:
        result = es.search(index=index_name, body={"query": query_info["query"]})
        print(f"🔍 {query_info['name']}: {result['hits']['total']['value']}개")
        
        # 상위 3개 결과 표시
        for hit in result['hits']['hits'][:3]:
            doc = hit['_source']
            print(f"   - {doc['title']} (가격: {doc['price']:,}원, 평점: {doc['rating']})")
    
    # 9. 스크롤 API 테스트 (대량 데이터 조회)
    print_section("스크롤 API 테스트")
    
    scroll_query = {
        "query": {"match_all": {}},
        "size": 20  # 한 번에 20개씩
    }
    
    result = es.search(index=index_name, body=scroll_query, scroll='2m')
    scroll_id = result['_scroll_id']
    
    total_processed = 0
    while len(result['hits']['hits']) > 0:
        total_processed += len(result['hits']['hits'])
        
        # 다음 배치 가져오기
        result = es.scroll(scroll_id=scroll_id, scroll='2m')
        
        if len(result['hits']['hits']) == 0:
            break
    
    print(f"📜 스크롤로 처리된 문서 수: {total_processed}개")
    
    # 스크롤 컨텍스트 정리
    es.clear_scroll(scroll_id=scroll_id)
    
    print_section("✅ 벌크 인덱싱 실습 완료!")

if __name__ == "__main__":
    main() 