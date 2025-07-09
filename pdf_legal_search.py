from elasticsearch import Elasticsearch
import base64
import os
import json
import traceback
from pathlib import Path
import re
from datetime import datetime

# Elasticsearch 연결 설정
es = Elasticsearch(
    "http://localhost:9200",
    basic_auth=("elastic", "OBIpKj46")
)

def print_section(title):
    print("\n" + "="*60)
    print(f"⚖️ {title}")
    print("="*60)

def check_attachment_plugin():
    """Elasticsearch attachment 플러그인 설치 확인"""
    try:
        # Elasticsearch 9.x에서는 ingest-attachment가 기본 모듈로 포함됨
        # 테스트 파이프라인 생성해서 확인
        test_pipeline = {
            "processors": [
                {
                    "attachment": {
                        "field": "data"
                    }
                }
            ]
        }
        es.ingest.put_pipeline(id="test_attachment_check", body=test_pipeline)
        es.ingest.delete_pipeline(id="test_attachment_check")
        return True
    except Exception as e:
        print(f"Attachment processor 확인 중 오류: {e}")
        return False

def install_attachment_plugin():
    """Attachment 플러그인 설치 안내"""
    print("⚠️ Attachment 플러그인이 설치되어 있지 않습니다.")
    print("\n🔧 플러그인 설치 방법:")
    print("Docker 컨테이너에 접속하여 플러그인을 설치해야 합니다:")
    print("")
    print("1. Docker 컨테이너 접속:")
    print("   docker exec -it elasticsearch bash")
    print("")
    print("2. 플러그인 설치:")
    print("   bin/elasticsearch-plugin install ingest-attachment")
    print("")
    print("3. 컨테이너 재시작:")
    print("   docker restart elasticsearch")
    print("")
    print("설치 후 다시 실행해주세요!")

def create_legal_pipeline():
    """법령 PDF 처리를 위한 고급 파이프라인 생성"""
    pipeline = {
        "description": "법령 PDF 텍스트 추출 및 분석을 위한 파이프라인",
        "processors": [
            {
                "attachment": {
                    "field": "data",
                    "target_field": "attachment",
                    "indexed_chars": -1,  # 모든 문자 인덱싱 (법령은 전체 내용이 중요)
                    "properties": ["content", "title", "author", "keywords", "content_type", "content_length", "language"],
                    "remove_binary": True,  # 메모리 절약을 위해 바이너리 제거
                    "ignore_missing": True  # 필드가 없어도 계속 진행
                }
            },
            {
                "remove": {
                    "field": "data",  # 원본 바이너리 데이터 제거
                    "ignore_missing": True
                }
            }
        ]
    }
    
    es.ingest.put_pipeline(id="legal_attachment", body=pipeline)
    print("✅ 법령 전용 파이프라인 생성 완료")

def create_legal_index():
    """법령 문서 전용 인덱스 생성"""
    index_name = "legal_documents"
    
    # 기존 인덱스 삭제
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
        print(f"🗑️ 기존 인덱스 '{index_name}' 삭제")
    
    # 법령 검색에 최적화된 매핑 설정
    mapping = {
        "settings": {
            "analysis": {
                "analyzer": {
                    "legal_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "stop",
                            "snowball"
                        ]
                    },
                    "exact_match": {
                        "type": "keyword"
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "filename": {
                    "type": "keyword"
                },
                "document_type": {
                    "type": "keyword"
                },
                "upload_date": {
                    "type": "date"
                },
                "file_size": {
                    "type": "long"
                },
                "legal_category": {
                    "type": "keyword"  # 스토킹, 형법, 민법 등
                },
                "attachment": {
                    "properties": {
                        "content": {
                            "type": "text",
                            "analyzer": "legal_analyzer",
                            "fields": {
                                "ngram": {
                                    "type": "text",
                                    "analyzer": "standard"
                                }
                            }
                        },
                        "title": {
                            "type": "text",
                            "analyzer": "legal_analyzer"
                        },
                        "keywords": {
                            "type": "text"
                        },
                        "content_type": {
                            "type": "keyword"
                        },
                        "content_length": {
                            "type": "integer"
                        },
                        "language": {
                            "type": "keyword"
                        }
                    }
                }
            }
        }
    }
    
    es.indices.create(index=index_name, body=mapping)
    print(f"✅ 법령 전용 인덱스 '{index_name}' 생성 완료")
    return index_name

def index_stalker_pdf(index_name):
    """stalker.pdf 파일을 인덱싱"""
    pdf_path = "stalker.pdf"
    
    try:
        if not os.path.exists(pdf_path):
            print(f"❌ 파일을 찾을 수 없습니다: {pdf_path}")
            print("📂 현재 위치:", os.getcwd())
            print("📁 디렉토리 내용:")
            for file in os.listdir('.'):
                if file.endswith('.pdf'):
                    print(f"   📄 {file}")
            return False
        
        print(f"📄 스토킹 법령 PDF 인덱싱 중: {pdf_path}")
        
        # PDF 파일을 base64로 인코딩
        with open(pdf_path, "rb") as f:
            pdf_data = base64.b64encode(f.read()).decode('utf-8')
        
        # 파일 정보
        file_size = os.path.getsize(pdf_path)
        
        # 법령 문서 메타데이터
        doc = {
            "filename": pdf_path,
            "document_type": "법령집",
            "legal_category": "스토킹범죄",
            "upload_date": datetime.now().isoformat(),
            "file_size": file_size,
            "data": pdf_data
        }
        
        # 법령 전용 파이프라인으로 인덱싱
        result = es.index(
            index=index_name,
            body=doc,
            pipeline="legal_attachment"
        )
        
        print(f"✅ 스토킹 법령 PDF 인덱싱 완료!")
        print(f"   📁 파일명: {pdf_path}")
        print(f"   📏 크기: {file_size:,} bytes")
        print(f"   🆔 문서 ID: {result['_id']}")
        return True
        
    except Exception as e:
        print(f"❌ PDF 인덱싱 실패: {e}")
        traceback.print_exc()
        return False

def search_legal_content(query, index_name, search_type="standard"):
    """법령 내용에서 키워드 검색 - Ctrl+F 스타일"""
    
    if search_type == "exact":
        # 정확한 구문 검색 (따옴표 검색)
        search_body = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "match_phrase": {
                                "attachment.content": {
                                    "query": query,
                                    "boost": 3.0
                                }
                            }
                        },
                        {
                            "term": {
                                "attachment.content.exact": {
                                    "value": query,
                                    "boost": 2.0
                                }
                            }
                        }
                    ]
                }
            },
            "highlight": {
                "fields": {
                    "attachment.content": {
                        "fragment_size": 200,
                        "number_of_fragments": 5,
                        "pre_tags": ["<mark>"],
                        "post_tags": ["</mark>"]
                    }
                },
                "require_field_match": False
            },
            "_source": ["filename", "legal_category", "file_size", "upload_date"]
        }
    else:
        # 표준 검색 (단어 매칭)
        search_body = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "match": {
                                "attachment.content": {
                                    "query": query,
                                    "boost": 2.0,
                                    "operator": "and"
                                }
                            }
                        },
                        {
                            "match": {
                                "attachment.content.ngram": {
                                    "query": query,
                                    "boost": 1.5
                                }
                            }
                        },
                        {
                            "wildcard": {
                                "attachment.content": {
                                    "value": f"*{query}*",
                                    "boost": 1.0
                                }
                            }
                        }
                    ]
                }
            },
            "highlight": {
                "fields": {
                    "attachment.content": {
                        "fragment_size": 200,
                        "number_of_fragments": 5,
                        "pre_tags": ["<mark>"],
                        "post_tags": ["</mark>"]
                    }
                },
                "require_field_match": False
            },
            "_source": ["filename", "legal_category", "file_size", "upload_date"]
        }
    
    try:
        result = es.search(index=index_name, body=search_body)
        return result
    except Exception as e:
        print(f"❌ 검색 실패: {e}")
        return None

def display_search_results(query, result, search_type="standard"):
    """검색 결과를 보기 좋게 표시"""
    if not result or result['hits']['total']['value'] == 0:
        print(f"📭 '{query}'에 대한 검색 결과가 없습니다.")
        return
    
    total_hits = result['hits']['total']['value']
    print(f"\n📊 '{query}' 검색 결과: {total_hits}개 일치")
    
    if search_type == "exact":
        print("🔍 정확한 구문 검색 결과")
    else:
        print("🔍 표준 키워드 검색 결과")
    
    for i, hit in enumerate(result['hits']['hits'], 1):
        print(f"\n{i}. 📄 {hit['_source']['filename']}")
        print(f"   ⚖️ 분류: {hit['_source'].get('legal_category', '미분류')}")
        print(f"   ⭐ 관련도: {hit['_score']:.2f}")
        
        # 하이라이트된 내용 표시
        if 'highlight' in hit and 'attachment.content' in hit['highlight']:
            print("   💡 일치하는 조문/내용:")
            for j, fragment in enumerate(hit['highlight']['attachment.content'][:3], 1):
                # HTML 태그 제거하고 텍스트만 표시
                clean_fragment = fragment.replace('<mark>', '【').replace('</mark>', '】')
                print(f"      {j}. {clean_fragment}")
        
        print("   " + "-" * 50)

def legal_quick_search(index_name):
    """법령 빠른 검색 - Ctrl+F 스타일"""
    print_section("⚡ 법령 빠른 검색 (Ctrl+F 스타일)")
    print("🔍 검색 팁:")
    print("  • 일반 검색: 키워드 입력")
    print("  • 정확한 구문: \"따옴표로 감싸서 입력\"")
    print("  • 종료: 'quit', 'exit', '종료'")
    print("  • 도움말: 'help', '도움말'")
    
    search_history = []
    
    while True:
        query = input("\n🔍 검색어: ").strip()
        
        if query.lower() in ['quit', 'exit', '종료']:
            break
        elif query.lower() in ['help', '도움말']:
            show_help()
            continue
        elif not query:
            continue
        
        # 검색 기록 저장
        search_history.append(query)
        
        # 따옴표로 감싸진 경우 정확한 구문 검색
        if query.startswith('"') and query.endswith('"'):
            clean_query = query[1:-1]  # 따옴표 제거
            result = search_legal_content(clean_query, index_name, "exact")
            display_search_results(clean_query, result, "exact")
        else:
            result = search_legal_content(query, index_name, "standard")
            display_search_results(query, result, "standard")

def show_help():
    """도움말 표시"""
    print("\n📖 법령 검색 도움말")
    print("="*40)
    print("🔍 검색 방법:")
    print("  스토킹      → '스토킹' 키워드가 포함된 모든 조문")
    print("  \"스토킹범죄\"  → '스토킹범죄' 정확한 구문")
    print("  형법        → 형법 관련 조문")
    print("  처벌        → 처벌 관련 내용")
    print()
    print("💡 검색 예시:")
    print("  • 스토킹 정의 찾기: \"스토킹범죄의 정의\"")
    print("  • 처벌 조항: 처벌")
    print("  • 신고 방법: 신고")
    print("  • 보호 조치: \"보호조치\"")

def demo_legal_searches(index_name):
    """법령 검색 데모"""
    print_section("🎯 스토킹 법령 검색 데모")
    
    demo_queries = [
        ("스토킹", "스토킹 관련 조문 검색"),
        ("\"스토킹범죄\"", "스토킹범죄 정확한 용어 검색"),
        ("처벌", "처벌 관련 조항 검색"),
        ("신고", "신고 절차 관련 내용"),
        ("보호조치", "피해자 보호조치 관련")
    ]
    
    for query, description in demo_queries:
        print(f"\n🔎 {description}: '{query}'")
        
        if query.startswith('"') and query.endswith('"'):
            clean_query = query[1:-1]
            result = search_legal_content(clean_query, index_name, "exact")
            display_search_results(clean_query, result, "exact")
        else:
            result = search_legal_content(query, index_name, "standard")
            display_search_results(query, result, "standard")
        
        print()

def main():
    try:
        print_section("⚖️ 스토킹 법령 PDF 검색 시스템")
        print("📚 대한민국 스토킹 범죄 관련 5개 법령 모음집 검색")
        
        # 1. 연결 확인
        if not es.ping():
            print("❌ Elasticsearch 연결 실패")
            return
        print("✅ Elasticsearch 연결 성공")
        
        # 2. Attachment 플러그인 확인
        print_section("🔌 Attachment 플러그인 확인")
        if not check_attachment_plugin():
            install_attachment_plugin()
            return
        print("✅ Attachment 플러그인 설치 확인")
        
        # 3. 법령 전용 파이프라인 생성
        print_section("⚙️ 법령 전용 파이프라인 설정")
        create_legal_pipeline()
        
        # 4. 법령 전용 인덱스 생성
        print_section("📁 법령 전용 인덱스 생성")
        index_name = create_legal_index()
        
        # 5. stalker.pdf 인덱싱
        print_section("📄 스토킹 법령 PDF 인덱싱")
        if not index_stalker_pdf(index_name):
            print("❌ stalker.pdf 인덱싱에 실패했습니다.")
            return
        
        # 인덱스 새로고침
        es.indices.refresh(index=index_name)
        print("🔄 인덱스 새로고침 완료")
        
        # 6. 검색 데모
        demo_legal_searches(index_name)
        
        # 7. 대화형 검색 (Ctrl+F 스타일)
        legal_quick_search(index_name)
        
        print_section("✅ 법령 검색 시스템 완료!")
        print("🎉 씹고수님, 이제 법령도 척척 검색하시네요!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        print("상세 오류 정보:")
        traceback.print_exc()

if __name__ == "__main__":
    main() 