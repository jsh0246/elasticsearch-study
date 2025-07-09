from elasticsearch import Elasticsearch
import json

# Elasticsearch 연결 설정
es = Elasticsearch(
    "http://localhost:9200",
    basic_auth=("elastic", "OBIpKj46")
)

def print_section(title):
    print("\n" + "="*50)
    print(f"🔍 {title}")
    print("="*50)

def print_search_results(result, title):
    print(f"📊 {title}: {result['hits']['total']['value']}개")
    for hit in result['hits']['hits']:
        score = hit.get('_score', 0)
        source = hit['_source']
        print(f"  - {source['title']} (작가: {source['author']}, 점수: {score:.2f})")

def main():
    index_name = "books"
    
    # 현재 저장된 데이터 확인
    print_section("현재 저장된 데이터 확인")
    all_docs = es.search(index=index_name, body={"query": {"match_all": {}}})
    
    for hit in all_docs['hits']['hits']:
        doc = hit['_source']
        print(f"ID: {hit['_id']}")
        print(f"  제목: {doc['title']}")
        print(f"  작가: {doc['author']}")
        print(f"  설명: {doc['description']}")
        print(f"  가격: {doc['price']:,}원")
        print()

    # 1. 한국어 부분 매칭 검색
    print_section("1. 한국어 부분 매칭 검색")
    
    korean_queries = [
        ("제목에서 '머신러닝' 검색", {"match": {"title": "머신러닝"}}),
        ("제목에서 '웹' 검색", {"match": {"title": "웹"}}),
        ("제목에서 'Django' 검색", {"match": {"title": "Django"}}),
        ("설명에서 '입문서' 검색", {"match": {"description": "입문서"}}),
        ("설명에서 '애플리케이션' 검색", {"match": {"description": "애플리케이션"}}),
        ("설명에서 '엔진' 검색", {"match": {"description": "엔진"}}),
    ]
    
    for desc, query in korean_queries:
        result = es.search(index=index_name, body={"query": query})
        print_search_results(result, desc)
    
    # 2. 정확한 구문 검색
    print_section("2. 정확한 구문 검색")
    
    phrase_queries = [
        ("'Python을 사용한' 구문 검색", {"match_phrase": {"description": "Python을 사용한"}}),
        ("'웹 애플리케이션' 구문 검색", {"match_phrase": {"description": "웹 애플리케이션"}}),
        ("'검색 엔진' 구문 검색", {"match_phrase": {"description": "검색 엔진"}}),
    ]
    
    for desc, query in phrase_queries:
        result = es.search(index=index_name, body={"query": query})
        print_search_results(result, desc)
    
    # 3. 접두사 검색
    print_section("3. 접두사 검색")
    
    prefix_queries = [
        ("제목에서 'Python' 접두사 검색", {"prefix": {"title": "Python"}}),
        ("제목에서 'Django' 접두사 검색", {"prefix": {"title": "Django"}}),
        ("제목에서 'Elastic' 접두사 검색", {"prefix": {"title": "Elastic"}}),
    ]
    
    for desc, query in prefix_queries:
        result = es.search(index=index_name, body={"query": query})
        print_search_results(result, desc)
    
    # 4. 와일드카드 검색 (한국어 포함)
    print_section("4. 와일드카드 검색")
    
    wildcard_queries = [
        ("제목에서 '*Python*' 와일드카드 검색", {"wildcard": {"title": "*Python*"}}),
        ("제목에서 '*웹*' 와일드카드 검색", {"wildcard": {"title": "*웹*"}}),
        ("설명에서 '*Python*' 와일드카드 검색", {"wildcard": {"description": "*Python*"}}),
    ]
    
    for desc, query in wildcard_queries:
        result = es.search(index=index_name, body={"query": query})
        print_search_results(result, desc)
    
    # 5. 복잡한 불린 쿼리
    print_section("5. 복잡한 불린 쿼리")
    
    complex_query = {
        "query": {
            "bool": {
                "should": [
                    {"match": {"title": "Python"}},
                    {"match": {"description": "Python"}},
                    {"match": {"title": "웹"}},
                    {"match": {"description": "웹"}}
                ],
                "must": [
                    {"range": {"price": {"gte": 20000}}}
                ],
                "must_not": [
                    {"match": {"author": "없는작가"}}
                ]
            }
        }
    }
    
    result = es.search(index=index_name, body=complex_query)
    print_search_results(result, "복합 불린 쿼리")
    
    # 6. 상세한 집계 분석
    print_section("6. 상세한 집계 분석")
    
    detailed_agg = {
        "size": 0,
        "aggs": {
            "price_ranges": {
                "range": {
                    "field": "price",
                    "ranges": [
                        {"to": 30000},
                        {"from": 30000, "to": 40000},
                        {"from": 40000}
                    ]
                }
            },
            "page_stats": {
                "extended_stats": {
                    "field": "pages"
                }
            },
            "authors_with_books": {
                "terms": {
                    "field": "author",
                    "size": 10
                },
                "aggs": {
                    "avg_price": {
                        "avg": {
                            "field": "price"
                        }
                    }
                }
            }
        }
    }
    
    result = es.search(index=index_name, body=detailed_agg)
    aggs = result['aggregations']
    
    print("💰 가격 범위별 분포:")
    for bucket in aggs['price_ranges']['buckets']:
        key = bucket['key']
        count = bucket['doc_count']
        if 'to' in bucket and 'from' not in bucket:
            print(f"  - {bucket['to']:,}원 미만: {count}권")
        elif 'from' in bucket and 'to' in bucket:
            print(f"  - {bucket['from']:,}원 ~ {bucket['to']:,}원: {count}권")
        elif 'from' in bucket and 'to' not in bucket:
            print(f"  - {bucket['from']:,}원 이상: {count}권")
    
    page_stats = aggs['page_stats']
    print(f"\n📖 페이지 통계:")
    print(f"  - 평균: {page_stats['avg']:.0f}페이지")
    print(f"  - 최소: {page_stats['min']:.0f}페이지")
    print(f"  - 최대: {page_stats['max']:.0f}페이지")
    print(f"  - 표준편차: {page_stats['std_deviation']:.0f}")
    
    print(f"\n👥 작가별 평균 가격:")
    for bucket in aggs['authors_with_books']['buckets']:
        author = bucket['key']
        count = bucket['doc_count']
        avg_price = bucket['avg_price']['value']
        print(f"  - {author}: {count}권, 평균 {avg_price:,.0f}원")
    
    # 7. 하이라이트 검색 (수정된 버전)
    print_section("7. 하이라이트 검색")
    
    highlight_query = {
        "query": {
            "multi_match": {
                "query": "Python 웹 검색",
                "fields": ["title", "description"]
            }
        },
        "highlight": {
            "fields": {
                "title": {},
                "description": {}
            }
        }
    }
    
    result = es.search(index=index_name, body=highlight_query)
    print(f"📊 하이라이트 검색 결과: {result['hits']['total']['value']}개")
    
    for hit in result['hits']['hits']:
        source = hit['_source']
        highlights = hit.get('highlight', {})
        print(f"  - {source['title']} (점수: {hit['_score']:.2f})")
        
        if 'title' in highlights:
            print(f"    제목 하이라이트: {highlights['title'][0]}")
        if 'description' in highlights:
            print(f"    설명 하이라이트: {highlights['description'][0]}")

if __name__ == "__main__":
    main() 