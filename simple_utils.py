from elasticsearch import Elasticsearch
import json

# Elasticsearch 연결 설정
es = Elasticsearch(
    "http://localhost:9200",
    basic_auth=("elastic", "OBIpKj46")
)

def main():
    print("🔍 Elasticsearch 간단 유틸리티")
    print("=" * 50)
    
    # 1. 클러스터 기본 정보
    print("\n📊 클러스터 상태:")
    health = es.cluster.health()
    print(f"  - 상태: {health['status']}")
    print(f"  - 노드 수: {health['number_of_nodes']}")
    print(f"  - 활성 샤드: {health['active_shards']}")
    
    # 2. books 인덱스 확인
    print("\n📚 books 인덱스 정보:")
    index_name = "books"
    
    if es.indices.exists(index=index_name):
        # 문서 수 확인
        count = es.count(index=index_name)
        print(f"  - 문서 수: {count['count']}개")
        
        # 매핑 확인
        mapping = es.indices.get_mapping(index=index_name)
        properties = mapping[index_name]['mappings']['properties']
        print(f"  - 필드 수: {len(properties)}개")
        print(f"  - 필드 목록: {list(properties.keys())}")
        
        # 샘플 문서 1개 조회
        sample = es.search(index=index_name, body={"query": {"match_all": {}}, "size": 1})
        if sample['hits']['hits']:
            doc = sample['hits']['hits'][0]['_source']
            print(f"  - 샘플 문서: {doc['title']}")
    else:
        print("  - 인덱스가 존재하지 않습니다.")
    
    # 3. 간단한 검색 테스트
    print("\n🔍 간단한 검색 테스트:")
    
    if es.indices.exists(index=index_name):
        # 전체 문서 검색
        all_docs = es.search(index=index_name, body={"query": {"match_all": {}}})
        print(f"  - 전체 문서: {all_docs['hits']['total']['value']}개")
        
        # 키워드 검색
        search_results = es.search(index=index_name, body={
            "query": {"match": {"title": "Python"}}
        })
        print(f"  - 'Python' 검색: {search_results['hits']['total']['value']}개")
        
        # 범위 검색
        price_results = es.search(index=index_name, body={
            "query": {"range": {"price": {"gte": 30000}}}
        })
        print(f"  - 3만원 이상: {price_results['hits']['total']['value']}개")
    
    # 4. 인덱스 목록 (시스템 인덱스 제외)
    print("\n📁 사용자 인덱스 목록:")
    indices = es.cat.indices(format='json')
    user_indices = [idx for idx in indices if not idx['index'].startswith('.')]
    
    for idx in user_indices[:5]:  # 최대 5개만 표시
        print(f"  - {idx['index']}: {idx['docs.count']}개 문서")
    
    print("\n✅ 유틸리티 완료!")

if __name__ == "__main__":
    main() 