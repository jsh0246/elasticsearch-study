#!/usr/bin/env python3
"""
빠른 테스트 스크립트 - Elasticsearch 연결 확인
"""

from elasticsearch import Elasticsearch
import sys
import traceback

def test_elasticsearch():
    """Elasticsearch 연결 테스트"""
    print("🔍 Elasticsearch 연결 테스트 시작...")
    
    try:
        # Elasticsearch 연결
        es = Elasticsearch(
            "http://localhost:9200",
            basic_auth=("elastic", "OBIpKj46")
        )
        
        # 연결 확인
        if es.ping():
            print("✅ Elasticsearch 연결 성공!")
            
            # 클러스터 정보
            info = es.info()
            print(f"📊 클러스터: {info['cluster_name']}")
            print(f"🔢 버전: {info['version']['number']}")
            
            # attachment 플러그인 확인
            plugins = es.cat.plugins(format="json")
            has_attachment = any(plugin.get('component') == 'ingest-attachment' for plugin in plugins)
            
            if has_attachment:
                print("✅ attachment 플러그인 설치됨")
            else:
                print("⚠️  attachment 플러그인이 없습니다")
                print("   설치 명령어: bin/elasticsearch-plugin install ingest-attachment")
            
            return True
            
        else:
            print("❌ Elasticsearch 연결 실패")
            return False
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return False

def test_imports():
    """필요한 모듈 import 테스트"""
    print("\n📦 모듈 import 테스트...")
    
    try:
        import elasticsearch
        print("✅ elasticsearch 모듈")
        
        import base64
        print("✅ base64 모듈")
        
        import json
        print("✅ json 모듈")
        
        try:
            import reportlab
            print("✅ reportlab 모듈")
        except ImportError:
            print("⚠️  reportlab 모듈 없음 (PDF 생성 기능에 필요)")
            
        return True
        
    except Exception as e:
        print(f"❌ 모듈 import 오류: {e}")
        return False

def check_pdf_file():
    """PDF 파일 존재 확인"""
    print("\n📄 PDF 파일 확인...")
    
    import os
    
    if os.path.exists('stalker.pdf'):
        size = os.path.getsize('stalker.pdf')
        print(f"✅ stalker.pdf 존재 (크기: {size:,} bytes)")
        return True
    else:
        print("❌ stalker.pdf 파일이 없습니다")
        return False

def main():
    """메인 테스트 함수"""
    print("="*60)
    print("🧪 법령 검색 시스템 빠른 테스트")
    print("="*60)
    
    # 모든 테스트 실행
    tests = [
        ("모듈 Import", test_imports),
        ("PDF 파일", check_pdf_file),
        ("Elasticsearch 연결", test_elasticsearch),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        results[test_name] = test_func()
    
    # 결과 요약
    print("\n" + "="*60)
    print("📊 테스트 결과 요약")
    print("="*60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ 통과" if passed else "❌ 실패"
        print(f"{test_name:20} : {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 모든 테스트 통과! 법령 검색 시스템 실행 준비 완료!")
        print("\n실행 명령어:")
        print("  uv run python pdf_legal_search.py")
    else:
        print("⚠️  일부 테스트 실패. 위의 오류를 먼저 해결해주세요.")
    print("="*60)

if __name__ == "__main__":
    main() 