from elasticsearch import Elasticsearch
import json

# Elasticsearch 연결 설정
es = Elasticsearch(
    "http://localhost:9200",
    basic_auth=("elastic", "OBIpKj46")
)

def print_section(title):
    print("\n" + "="*60)
    print(f"🔍 {title}")
    print("="*60)

def search_books(query_text, filters=None, sort_by=None, page=1, size=10):
    """실제 검색 서비스와 같은 검색 함수"""
    
    # 기본 검색 쿼리 구성
    search_query = {
        "query": {
            "bool": {
                "must": [],
                "filter": []
            }
        },
        "highlight": {
            "fields": {
                "title": {"number_of_fragments": 1},
                "description": {"number_of_fragments": 2}
            }
        },
        "from": (page - 1) * size,
        "size": size
    }
    
    # 텍스트 검색 쿼리
    if query_text:
        text_query = {
            "multi_match": {
                "query": query_text,
                "fields": ["title^3", "description^2", "author^2", "category"],
                "fuzziness": "AUTO",
                "operator": "and"
            }
        }
        search_query["query"]["bool"]["must"].append(text_query)
    else:
        search_query["query"]["bool"]["must"].append({"match_all": {}})
    
    # 필터 적용
    if filters:
        if "category" in filters:
            search_query["query"]["bool"]["filter"].append(
                {"term": {"category": filters["category"]}}
            )
        if "language" in filters:
            search_query["query"]["bool"]["filter"].append(
                {"term": {"language": filters["language"]}}
            )
        if "price_range" in filters:
            search_query["query"]["bool"]["filter"].append(
                {"range": {"price": filters["price_range"]}}
            )
        if "rating_min" in filters:
            search_query["query"]["bool"]["filter"].append(
                {"range": {"rating": {"gte": filters["rating_min"]}}}
            )
        if "publish_year" in filters:
            search_query["query"]["bool"]["filter"].append(
                {"range": {"publish_date": {"gte": f"{filters['publish_year']}-01-01"}}}
            )
    
    # 정렬 적용
    if sort_by:
        if sort_by == "price_asc":
            search_query["sort"] = [{"price": {"order": "asc"}}]
        elif sort_by == "price_desc":
            search_query["sort"] = [{"price": {"order": "desc"}}]
        elif sort_by == "rating_desc":
            search_query["sort"] = [{"rating": {"order": "desc"}}]
        elif sort_by == "newest":
            search_query["sort"] = [{"publish_date": {"order": "desc"}}]
        elif sort_by == "pages_desc":
            search_query["sort"] = [{"pages": {"order": "desc"}}]
    
    return es.search(index="tech_books", body=search_query)

def display_search_results(result, query_text=""):
    """검색 결과를 보기 좋게 표시"""
    total = result['hits']['total']['value']
    took = result['took']
    
    print(f"📊 검색 결과: {total}개 (검색 시간: {took}ms)")
    
    if query_text:
        print(f"🔍 검색어: '{query_text}'")
    
    if total == 0:
        print("❌ 검색 결과가 없습니다.")
        return
    
    print("\n📚 검색 결과:")
    print("-" * 60)
    
    for i, hit in enumerate(result['hits']['hits'], 1):
        doc = hit['_source']
        score = hit.get('_score', 0)
        
        print(f"{i}. {doc['title']} ⭐ {doc['rating']}")
        print(f"   작가: {doc['author']} | 카테고리: {doc['category']} | 언어: {doc['language']}")
        print(f"   가격: {doc['price']:,}원 | 페이지: {doc['pages']}p | 출간: {doc['publish_date']}")
        
        # 하이라이트 표시
        if 'highlight' in hit:
            for field, highlights in hit['highlight'].items():
                print(f"   📝 {field}: {highlights[0]}")
        
        if score is not None:
            print(f"   점수: {score:.2f}")
        else:
            print("   점수: N/A (정렬됨)")
        print()

def get_search_suggestions(query_text, size=5):
    """검색 제안 (자동완성 기능)"""
    
    suggestion_query = {
        "suggest": {
            "title_suggestion": {
                "prefix": query_text,
                "completion": {
                    "field": "title.suggest",
                    "size": size
                }
            }
        }
    }
    
    # 간단한 접두사 검색으로 대체
    prefix_query = {
        "query": {
            "bool": {
                "should": [
                    {"match_phrase_prefix": {"title": query_text}},
                    {"prefix": {"category": query_text}},
                    {"prefix": {"language": query_text}}
                ]
            }
        },
        "size": size,
        "_source": ["title", "category", "language"]
    }
    
    return es.search(index="tech_books", body=prefix_query)

def get_facets():
    """패싯 정보 가져오기 (필터 옵션)"""
    
    facet_query = {
        "size": 0,
        "aggs": {
            "categories": {
                "terms": {
                    "field": "category",
                    "size": 20
                }
            },
            "languages": {
                "terms": {
                    "field": "language",
                    "size": 20
                }
            },
            "price_ranges": {
                "range": {
                    "field": "price",
                    "ranges": [
                        {"key": "저가", "to": 25000},
                        {"key": "중간", "from": 25000, "to": 40000},
                        {"key": "고가", "from": 40000}
                    ]
                }
            },
            "rating_ranges": {
                "range": {
                    "field": "rating",
                    "ranges": [
                        {"key": "3점 이상", "from": 3.0},
                        {"key": "4점 이상", "from": 4.0},
                        {"key": "4.5점 이상", "from": 4.5}
                    ]
                }
            }
        }
    }
    
    return es.search(index="tech_books", body=facet_query)

def main():
    print_section("실제 검색 서비스 시뮬레이션")
    
    # 1. 기본 검색
    print_section("1. 기본 텍스트 검색")
    
    search_queries = [
        "Python 머신러닝",
        "웹개발",
        "JavaScript",
        "데이터사이언스"
    ]
    
    for query in search_queries:
        print(f"\n🔍 '{query}' 검색:")
        result = search_books(query, size=3)
        display_search_results(result, query)
    
    # 2. 필터링 검색
    print_section("2. 필터링 검색")
    
    filter_examples = [
        {
            "query": "Python",
            "filters": {"category": "머신러닝", "rating_min": 4.0},
            "description": "Python + 머신러닝 카테고리 + 평점 4.0 이상"
        },
        {
            "query": "",
            "filters": {"price_range": {"gte": 30000, "lte": 40000}},
            "description": "가격 3만~4만원 범위"
        },
        {
            "query": "웹",
            "filters": {"language": "JavaScript", "publish_year": 2023},
            "description": "웹 + JavaScript + 2023년 이후"
        }
    ]
    
    for example in filter_examples:
        print(f"\n🔍 {example['description']}:")
        result = search_books(example["query"], example["filters"], size=3)
        display_search_results(result, example["query"])
    
    # 3. 정렬 검색
    print_section("3. 정렬 검색")
    
    sort_examples = [
        ("", "price_asc", "가격 낮은순"),
        ("", "rating_desc", "평점 높은순"),
        ("", "newest", "최신순"),
        ("Python", "price_desc", "Python 관련 도서 - 가격 높은순")
    ]
    
    for query, sort_by, description in sort_examples:
        print(f"\n🔍 {description}:")
        result = search_books(query, sort_by=sort_by, size=3)
        display_search_results(result, query)
    
    # 4. 페이지네이션 테스트
    print_section("4. 페이지네이션 테스트")
    
    query = "프로그래밍"
    page_size = 5
    
    for page in range(1, 4):  # 1, 2, 3 페이지
        print(f"\n📄 '{query}' 검색 - {page}페이지 (페이지당 {page_size}개):")
        result = search_books(query, page=page, size=page_size)
        
        if result['hits']['hits']:
            print(f"   총 {result['hits']['total']['value']}개 중 {(page-1)*page_size + 1}~{min(page*page_size, result['hits']['total']['value'])}번째:")
            for i, hit in enumerate(result['hits']['hits'], 1):
                doc = hit['_source']
                print(f"   {(page-1)*page_size + i}. {doc['title']} ({doc['price']:,}원)")
        else:
            print("   더 이상 결과가 없습니다.")
    
    # 5. 검색 제안 (자동완성)
    print_section("5. 검색 제안")
    
    suggestion_queries = ["Pyt", "웹", "머신", "Java"]
    
    for query in suggestion_queries:
        print(f"\n💡 '{query}' 입력 시 제안:")
        result = get_search_suggestions(query)
        
        if result['hits']['hits']:
            for hit in result['hits']['hits']:
                doc = hit['_source']
                print(f"   - {doc['title']} ({doc['category']})")
        else:
            print("   제안할 내용이 없습니다.")
    
    # 6. 패싯 정보 (필터 옵션)
    print_section("6. 패싯 정보 (필터 옵션)")
    
    facet_result = get_facets()
    aggs = facet_result['aggregations']
    
    print("📊 카테고리별 분포:")
    for bucket in aggs['categories']['buckets']:
        print(f"   {bucket['key']}: {bucket['doc_count']}개")
    
    print("\n💻 언어별 분포:")
    for bucket in aggs['languages']['buckets']:
        print(f"   {bucket['key']}: {bucket['doc_count']}개")
    
    print("\n💰 가격대별 분포:")
    for bucket in aggs['price_ranges']['buckets']:
        print(f"   {bucket['key']}: {bucket['doc_count']}개")
    
    print("\n⭐ 평점별 분포:")
    for bucket in aggs['rating_ranges']['buckets']:
        print(f"   {bucket['key']}: {bucket['doc_count']}개")
    
    # 7. 복합 시나리오 테스트
    print_section("7. 복합 시나리오 테스트")
    
    print("🛒 시나리오: 예산 3만원 이하, 평점 4.0 이상, Python 관련 도서를 최신순으로 검색")
    
    result = search_books(
        query_text="Python",
        filters={
            "price_range": {"lte": 30000},
            "rating_min": 4.0
        },
        sort_by="newest",
        size=5
    )
    
    display_search_results(result, "Python")
    
    print_section("✅ 실제 검색 서비스 시뮬레이션 완료!")

if __name__ == "__main__":
    main() 