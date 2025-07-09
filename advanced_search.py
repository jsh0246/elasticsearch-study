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
    
    # 1. 부분 텍스트 검색
    print_section("1. 부분 텍스트 검색")
    queries = [
        ("제목에서 '머신러닝' 검색", {"match": {"title": "머신러닝"}}),
        ("제목에서 '웹' 검색", {"match": {"title": "웹"}}),
        ("설명에서 'Python' 검색", {"match": {"description": "Python"}}),
        ("설명에서 '검색' 검색", {"match": {"description": "검색"}}),
    ]
    
    for desc, query in queries:
        result = es.search(index=index_name, body={"query": query})
        print_search_results(result, desc)
    
    # 2. 퍼지 검색 (오타 허용)
    print_section("2. 퍼지 검색")
    fuzzy_query = {
        "query": {
            "fuzzy": {
                "title": {
                    "value": "파이썬",  # Python의 한글 표기
                    "fuzziness": "AUTO"
                }
            }
        }
    }
    
    result = es.search(index=index_name, body=fuzzy_query)
    print_search_results(result, "퍼지 검색 - '파이썬'")
    
    # 3. 와일드카드 검색
    print_section("3. 와일드카드 검색")
    wildcard_query = {
        "query": {
            "wildcard": {
                "title": "*Python*"
            }
        }
    }
    
    result = es.search(index=index_name, body=wildcard_query)
    print_search_results(result, "와일드카드 검색 - '*Python*'")
    
    # 4. 정확한 키워드 검색
    print_section("4. 정확한 키워드 검색")
    term_query = {
        "query": {
            "term": {
                "author": "김철수"
            }
        }
    }
    
    result = es.search(index=index_name, body=term_query)
    print_search_results(result, "정확한 키워드 검색 - 작가: 김철수")
    
    # 5. 다중 필드 검색
    print_section("5. 다중 필드 검색")
    multi_match_query = {
        "query": {
            "multi_match": {
                "query": "Python",
                "fields": ["title^2", "description"]  # title에 가중치 2배
            }
        }
    }
    
    result = es.search(index=index_name, body=multi_match_query)
    print_search_results(result, "다중 필드 검색 - 'Python'")
    
    # 6. 불린 쿼리 조합
    print_section("6. 불린 쿼리 조합")
    bool_query = {
        "query": {
            "bool": {
                "should": [  # OR 조건
                    {"match": {"title": "Python"}},
                    {"match": {"description": "웹"}}
                ],
                "minimum_should_match": 1
            }
        }
    }
    
    result = es.search(index=index_name, body=bool_query)
    print_search_results(result, "불린 쿼리 - 'Python' OR '웹'")
    
    # 7. 날짜 범위 검색
    print_section("7. 날짜 범위 검색")
    date_range_query = {
        "query": {
            "range": {
                "publish_date": {
                    "gte": "2023-01-01",
                    "lte": "2023-03-31"
                }
            }
        }
    }
    
    result = es.search(index=index_name, body=date_range_query)
    print_search_results(result, "날짜 범위 검색 - 2023년 1-3월")
    
    # 8. 정렬된 검색
    print_section("8. 정렬된 검색")
    sorted_query = {
        "query": {"match_all": {}},
        "sort": [
            {"price": {"order": "desc"}},
            {"pages": {"order": "asc"}}
        ]
    }
    
    result = es.search(index=index_name, body=sorted_query)
    print("📊 가격 내림차순, 페이지 오름차순 정렬:")
    for hit in result['hits']['hits']:
        source = hit['_source']
        print(f"  - {source['title']} (가격: {source['price']:,}원, 페이지: {source['pages']})")
    
    # 9. 집계와 검색 조합
    print_section("9. 집계와 검색 조합")
    agg_search_query = {
        "query": {
            "range": {
                "price": {"gte": 25000}
            }
        },
        "aggs": {
            "price_stats": {
                "stats": {
                    "field": "price"
                }
            },
            "authors_count": {
                "cardinality": {
                    "field": "author"
                }
            }
        }
    }
    
    result = es.search(index=index_name, body=agg_search_query)
    print_search_results(result, "25,000원 이상 도서")
    
    if 'aggregations' in result:
        stats = result['aggregations']['price_stats']
        authors_count = result['aggregations']['authors_count']['value']
        print(f"💰 가격 통계:")
        print(f"  - 최소: {stats['min']:,}원")
        print(f"  - 최대: {stats['max']:,}원")
        print(f"  - 평균: {stats['avg']:,.0f}원")
        print(f"👥 작가 수: {authors_count}명")
    
    # 10. 하이라이트 검색
    print_section("10. 하이라이트 검색")
    highlight_query = {
        "query": {
            "match": {
                "description": "Python"
            }
        },
        "highlight": {
            "fields": {
                "description": {}
            }
        }
    }
    
    result = es.search(index=index_name, body=highlight_query)
    print(f"📊 하이라이트 검색 결과: {result['hits']['total']['value']}개")
    for hit in result['hits']['hits']:
        source = hit['_source']
        highlights = hit.get('highlight', {})
        print(f"  - {source['title']}")
        if 'description' in highlights:
            print(f"    하이라이트: {highlights['description'][0]}")

if __name__ == "__main__":
    main() 