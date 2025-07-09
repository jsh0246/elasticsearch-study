#!/usr/bin/env python3
"""
attachment processor 디버깅 스크립트
"""

from elasticsearch import Elasticsearch
import base64
import json
import traceback

# Elasticsearch 연결
es = Elasticsearch(
    "http://localhost:9200",
    basic_auth=("elastic", "OBIpKj46")
)

def check_plugins():
    """설치된 플러그인 확인"""
    print("🔍 설치된 플러그인 확인...")
    try:
        plugins = es.cat.plugins(format="json")
        print(f"설치된 플러그인: {len(plugins)}개")
        
        has_attachment = False
        for plugin in plugins:
            print(f"  - {plugin.get('component', 'unknown')}")
            if 'attachment' in plugin.get('component', '').lower():
                has_attachment = True
        
        if has_attachment:
            print("✅ attachment 관련 플러그인 발견")
        else:
            print("⚠️  attachment 플러그인이 없습니다")
            print("   ingest-attachment 플러그인 설치가 필요할 수 있습니다")
        
        return has_attachment
    except Exception as e:
        print(f"❌ 플러그인 확인 실패: {e}")
        return False

def test_simple_attachment():
    """간단한 attachment processor 테스트"""
    print("\n🧪 간단한 attachment processor 테스트...")
    
    try:
        # 간단한 파이프라인 생성
        pipeline = {
            "description": "테스트용 attachment processor",
            "processors": [
                {
                    "attachment": {
                        "field": "data",
                        "remove_binary": True
                    }
                }
            ]
        }
        
        # 파이프라인 생성
        es.ingest.put_pipeline(
            id="test-attachment",
            processors=pipeline["processors"],
            description=pipeline["description"]
        )
        print("✅ 테스트 파이프라인 생성 성공")
        
        # 간단한 텍스트 파일 테스트
        test_data = "Hello World 안녕하세요"
        encoded_data = base64.b64encode(test_data.encode()).decode()
        
        test_doc = {
            "data": encoded_data
        }
        
        # 테스트 인덱스에 문서 추가
        result = es.index(
            index="test-attachment-index",
            id="test-doc",
            document=test_doc,
            pipeline="test-attachment"
        )
        
        print("✅ 테스트 문서 인덱싱 성공")
        
        # 결과 확인
        es.indices.refresh(index="test-attachment-index")
        doc = es.get(index="test-attachment-index", id="test-doc")
        
        if 'attachment' in doc['_source']:
            print("✅ attachment processor가 정상 작동합니다!")
            print(f"   추출된 내용: {doc['_source']['attachment'].get('content', 'N/A')}")
            return True
        else:
            print("❌ attachment 데이터가 생성되지 않았습니다")
            return False
            
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        traceback.print_exc()
        return False

def cleanup():
    """테스트 데이터 정리"""
    try:
        es.indices.delete(index="test-attachment-index", ignore=[404])
        es.ingest.delete_pipeline(id="test-attachment", ignore=[404])
        print("🧹 테스트 데이터 정리 완료")
    except:
        pass

def main():
    print("="*60)
    print("🔧 attachment processor 진단 도구")
    print("="*60)
    
    if not es.ping():
        print("❌ Elasticsearch 연결 실패")
        return
    
    print("✅ Elasticsearch 연결 성공")
    
    # 1. 플러그인 확인
    has_plugins = check_plugins()
    
    # 2. 간단한 attachment 테스트
    if has_plugins:
        test_works = test_simple_attachment()
        
        if test_works:
            print("\n🎉 attachment processor가 정상 작동합니다!")
            print("   원래 코드에 다른 문제가 있을 수 있습니다.")
        else:
            print("\n⚠️  attachment processor에 문제가 있습니다.")
            print("   해결 방법:")
            print("   1. Elasticsearch를 재시작")
            print("   2. ingest-attachment 플러그인 설치 확인")
            print("   3. 기존 ingest-attachment 방식 사용")
    else:
        print("\n⚠️  attachment 플러그인이 설치되지 않았습니다.")
        print("   ingest-attachment 플러그인 설치가 필요합니다.")
    
    # 정리
    cleanup()

if __name__ == "__main__":
    main() 