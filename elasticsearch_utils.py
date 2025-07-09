from elasticsearch import Elasticsearch
import json

# Elasticsearch 연결 설정
es = Elasticsearch(
    "http://localhost:9200",
    basic_auth=("elastic", "OBIpKj46")
)

def print_section(title):
    print("\n" + "="*60)
    print(f"⚙️  {title}")
    print("="*60)

def main():
    print_section("Elasticsearch 클러스터 정보")
    
    # 1. 클러스터 상태 확인
    health = es.cluster.health()
    print(f"클러스터 상태: {health['status']}")
    print(f"노드 수: {health['number_of_nodes']}")
    print(f"데이터 노드 수: {health['number_of_data_nodes']}")
    print(f"활성 샤드 수: {health['active_shards']}")
    print(f"초기화 중 샤드: {health.get('initializing_shards', 0)}")
    print(f"재배치 중 샤드: {health.get('relocating_shards', 0)}")
    print(f"미할당 샤드: {health.get('unassigned_shards', 0)}")
    
    # 2. 모든 인덱스 목록 확인
    print_section("인덱스 목록")
    
    try:
        indices = es.cat.indices(format='json')
        print(f"총 {len(indices)}개의 인덱스 발견:")
        for idx in indices:
            print(f"  📁 {idx['index']}")
            print(f"     - 상태: {idx['status']}")
            print(f"     - 문서 수: {idx['docs.count']}")
            print(f"     - 크기: {idx['store.size']}")
            print(f"     - 주 샤드: {idx['pri']}")
            print(f"     - 복제본: {idx['rep']}")
            print()
    except Exception as e:
        print(f"인덱스 목록 조회 실패: {e}")
    
    # 3. books 인덱스 상세 정보
    print_section("books 인덱스 상세 정보")
    
    index_name = "books"
    
    if es.indices.exists(index=index_name):
        # 매핑 정보 확인
        mapping = es.indices.get_mapping(index=index_name)
        print("📋 매핑 정보:")
        print(json.dumps(mapping[index_name]['mappings'], indent=2, ensure_ascii=False))
        
        # 설정 정보 확인
        settings = es.indices.get_settings(index=index_name)
        print("\n⚙️ 설정 정보:")
        print(json.dumps(settings[index_name]['settings'], indent=2, ensure_ascii=False))
        
        # 인덱스 통계
        stats = es.indices.stats(index=index_name)
        index_stats = stats['indices'][index_name]
        print(f"\n📊 인덱스 통계:")
        print(f"  - 총 문서 수: {index_stats['total']['docs']['count']}")
        print(f"  - 삭제된 문서 수: {index_stats['total']['docs']['deleted']}")
        print(f"  - 저장 공간: {index_stats['total']['store']['size_in_bytes']} bytes")
        print(f"  - 인덱싱 작업: {index_stats['total']['indexing']['index_total']}")
        print(f"  - 검색 작업: {index_stats['total']['search']['query_total']}")
        
    else:
        print(f"❌ '{index_name}' 인덱스가 존재하지 않습니다.")
    
    # 4. 샘플 데이터 분석
    print_section("샘플 데이터 분석")
    
    if es.indices.exists(index=index_name):
        # 텀 벡터 분석 (특정 문서의 분석 결과)
        try:
            termvector = es.termvectors(
                index=index_name,
                id=1,
                fields=['title', 'description'],
                term_statistics=True,
                field_statistics=True
            )
            
            print("📝 문서 1번의 텀 벡터 분석:")
            if 'term_vectors' in termvector:
                for field, terms in termvector['term_vectors'].items():
                    print(f"\n  📄 {field} 필드:")
                    if 'terms' in terms:
                        for term, info in terms['terms'].items():
                            print(f"    - '{term}': 빈도수 {info['term_freq']}")
        except Exception as e:
            print(f"텀 벡터 분석 실패: {e}")
    
    # 5. 분석기 테스트
    print_section("분석기 테스트")
    
    test_texts = [
        "Python으로 배우는 머신러닝",
        "Django 웹 개발",
        "Elasticsearch 완벽 가이드"
    ]
    
    for text in test_texts:
        try:
            # 표준 분석기로 분석
            result = es.indices.analyze(
                index=index_name,
                body={
                    "analyzer": "standard",
                    "text": text
                }
            )
            
            tokens = [token['token'] for token in result['tokens']]
            print(f"📝 '{text}' 분석 결과:")
            print(f"   토큰: {tokens}")
            
        except Exception as e:
            print(f"분석 실패: {e}")
    
    # 6. 인덱스 별칭 확인
    print_section("인덱스 별칭 확인")
    
    try:
        aliases = es.cat.aliases(format='json')
        if aliases:
            print("📎 설정된 별칭:")
            for alias in aliases:
                print(f"  - {alias['alias']} → {alias['index']}")
        else:
            print("📎 설정된 별칭이 없습니다.")
    except Exception as e:
        print(f"별칭 조회 실패: {e}")
    
    # 7. 노드 정보
    print_section("노드 정보")
    
    try:
        nodes = es.cat.nodes(format='json')
        print(f"📡 총 {len(nodes)}개의 노드:")
        for node in nodes:
            print(f"  - {node['name']}")
            print(f"    IP: {node['ip']}")
            print(f"    역할: {node['node.role']}")
            print(f"    CPU 사용률: {node['cpu']}%")
            print(f"    메모리 사용률: {node['ram.percent']}%")
            print(f"    디스크 사용률: {node['disk.used_percent']}%")
            print()
    except Exception as e:
        print(f"노드 정보 조회 실패: {e}")
    
    # 8. 인덱스 템플릿 확인
    print_section("인덱스 템플릿 확인")
    
    try:
        templates = es.cat.templates(format='json')
        if templates:
            print("📄 인덱스 템플릿:")
            for template in templates:
                print(f"  - {template['name']}: {template['index_patterns']}")
        else:
            print("📄 인덱스 템플릿이 없습니다.")
    except Exception as e:
        print(f"템플릿 조회 실패: {e}")
    
    print_section("✅ 모든 유틸리티 확인 완료!")

if __name__ == "__main__":
    main() 