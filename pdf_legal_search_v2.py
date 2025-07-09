#!/usr/bin/env python3
"""
법령 전문 검색 시스템 v2.0
- attachment processor 사용
- 개선된 PDF 처리
- 더 효율적인 메모리 사용
"""

from elasticsearch import Elasticsearch
import base64
import json
import traceback
import os

# Elasticsearch 연결 설정
es = Elasticsearch(
    "http://localhost:9200",
    basic_auth=("elastic", "OBIpKj46")
)

def print_section(title):
    """섹션 제목 출력"""
    print("\n" + "="*60)
    print(f"⚖️  {title}")
    print("="*60)

def create_attachment_pipeline():
    """attachment processor를 사용한 ingest pipeline 생성"""
    print("🔧 attachment processor 파이프라인 생성 중...")
    
    pipeline_config = {
        "description": "법령 문서 PDF 처리를 위한 attachment processor",
        "processors": [
            {
                "attachment": {
                    "field": "data",
                    "properties": [
                        "content", 
                        "title", 
                        "content_type", 
                        "content_length",
                        "language"
                    ],
                    "indexed_chars": 1000000,  # 1MB 제한
                    "remove_binary": True  # 메모리 절약을 위해 바이너리 제거
                }
            },
            {
                "remove": {
                    "field": "data"  # 처리 후 원본 데이터 제거
                }
            }
        ]
    }
    
    try:
        es.ingest.put_pipeline(id="legal-attachment", processors=pipeline_config["processors"], description=pipeline_config["description"])
        print("✅ legal-attachment 파이프라인 생성 완료")
        return True
    except Exception as e:
        print(f"❌ 파이프라인 생성 실패: {e}")
        return False

def create_legal_index():
    """법령 문서 전용 인덱스 생성"""
    print("📚 법령 인덱스 생성 중...")
    
    index_name = "legal-documents-v2"
    
    # 기존 인덱스 삭제
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
        print(f"🗑️  기존 인덱스 '{index_name}' 삭제")
    
    # 인덱스 매핑 설정
    mapping = {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "analysis": {
                "analyzer": {
                    "legal_analyzer": {
                        "type": "standard",
                        "stopwords": "_none_"  # 법령에서는 모든 단어가 중요
                    }
                }
            }
        },
        "mappings": {
            "properties": {
                "filename": {
                    "type": "keyword"
                },
                "upload_date": {
                    "type": "date"
                },
                "attachment": {
                    "properties": {
                        "content": {
                            "type": "text",
                            "analyzer": "legal_analyzer",
                            "search_analyzer": "legal_analyzer",
                            "term_vector": "with_positions_offsets"  # 하이라이트용
                        },
                        "title": {
                            "type": "text",
                            "analyzer": "legal_analyzer"
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
    
    try:
        es.indices.create(index=index_name, mappings=mapping["mappings"], settings=mapping["settings"])
        print(f"✅ 인덱스 '{index_name}' 생성 완료")
        return True
    except Exception as e:
        print(f"❌ 인덱스 생성 실패: {e}")
        return False

def index_pdf_document(pdf_path, doc_id="stalker-laws"):
    """PDF 문서를 attachment processor로 인덱싱"""
    print(f"📄 PDF 문서 인덱싱: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF 파일을 찾을 수 없습니다: {pdf_path}")
        return False
    
    try:
        # PDF 파일을 base64로 인코딩
        with open(pdf_path, 'rb') as f:
            pdf_data = base64.b64encode(f.read()).decode('utf-8')
        
        file_size = os.path.getsize(pdf_path)
        print(f"📊 파일 크기: {file_size:,} bytes")
        
        # 문서 데이터 구성
        document = {
            "filename": os.path.basename(pdf_path),
            "upload_date": "2024-01-01T00:00:00",
            "data": pdf_data  # attachment processor가 처리할 base64 데이터
        }
        
        # attachment processor 파이프라인을 통해 인덱싱
        result = es.index(
            index="legal-documents-v2",
            id=doc_id,
            document=document,  # body 대신 document 사용
            pipeline="legal-attachment"  # 파이프라인 지정
        )
        
        print("✅ PDF 문서 인덱싱 완료")
        print(f"📍 문서 ID: {result['_id']}")
        
        # 인덱스 새로고침
        es.indices.refresh(index="legal-documents-v2")
        
        return True
        
    except Exception as e:
        print(f"❌ PDF 인덱싱 실패: {e}")
        traceback.print_exc()
        return False

def verify_indexing():
    """인덱싱 결과 확인"""
    print("🔍 인덱싱 결과 확인 중...")
    
    try:
        # 문서 가져오기
        result = es.get(index="legal-documents-v2", id="stalker-laws")
        
        if 'attachment' in result['_source']:
            attachment = result['_source']['attachment']
            print(f"✅ 문서 처리 완료:")
            print(f"   📄 제목: {attachment.get('title', 'N/A')}")
            print(f"   📝 콘텐츠 길이: {attachment.get('content_length', 0):,} 문자")
            print(f"   🔤 언어: {attachment.get('language', 'N/A')}")
            print(f"   📋 타입: {attachment.get('content_type', 'N/A')}")
            
            # 내용 미리보기
            content = attachment.get('content', '')
            if content:
                preview = content[:200] + "..." if len(content) > 200 else content
                print(f"   👁️  내용 미리보기: {preview}")
            
            return True
        else:
            print("❌ attachment 데이터가 없습니다")
            return False
            
    except Exception as e:
        print(f"❌ 확인 실패: {e}")
        return False

def search_legal_content(query, max_results=5):
    """법령 내용 검색"""
    
    # 구문 검색 vs 일반 검색 구분
    if query.startswith('"') and query.endswith('"'):
        # 정확한 구문 검색
        clean_query = query.strip('"')
        search_query = {
            "query": {
                "match_phrase": {
                    "attachment.content": {
                        "query": clean_query
                    }
                }
            },
            "highlight": {
                "fields": {
                    "attachment.content": {
                        "pre_tags": ["<mark>"],
                        "post_tags": ["</mark>"],
                        "fragment_size": 200,
                        "number_of_fragments": 3
                    }
                }
            },
            "size": max_results
        }
        search_type = f'정확한 구문 "{clean_query}"'
    else:
        # 일반 키워드 검색 (퍼지 포함)
        search_query = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "match": {
                                "attachment.content": {
                                    "query": query,
                                    "boost": 2.0
                                }
                            }
                        },
                        {
                            "match": {
                                "attachment.content": {
                                    "query": query,
                                    "fuzziness": "AUTO",
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
                        "pre_tags": ["<mark>"],
                        "post_tags": ["</mark>"],
                        "fragment_size": 200,
                        "number_of_fragments": 3
                    }
                }
            },
            "size": max_results
        }
        search_type = f'키워드 "{query}"'
    
    try:
        result = es.search(index="legal-documents-v2", **search_query)
        hits = result['hits']['hits']
        
        print(f"\n🔍 {search_type} 검색 결과: {len(hits)}개 발견")
        print("="*80)
        
        if hits:
            for i, hit in enumerate(hits, 1):
                score = hit['_score']
                print(f"\n📋 결과 {i} (관련도: {score:.2f})")
                print("-" * 50)
                
                # 하이라이트된 내용 표시
                if 'highlight' in hit and 'attachment.content' in hit['highlight']:
                    for fragment in hit['highlight']['attachment.content']:
                        # HTML 태그를 보기 좋게 변환
                        display_fragment = fragment.replace('<mark>', '【').replace('</mark>', '】')
                        print(f"💡 {display_fragment}")
                        print()
                else:
                    # 하이라이트가 없는 경우 원본 내용의 일부 표시
                    content = hit['_source']['attachment']['content']
                    # 검색어가 포함된 부분 찾기
                    query_lower = query.lower().strip('"')
                    content_lower = content.lower()
                    
                    if query_lower in content_lower:
                        start_pos = content_lower.find(query_lower)
                        start = max(0, start_pos - 100)
                        end = min(len(content), start_pos + len(query_lower) + 100)
                        snippet = content[start:end]
                        
                        if start > 0:
                            snippet = "..." + snippet
                        if end < len(content):
                            snippet = snippet + "..."
                            
                        print(f"📝 {snippet}")
                        print()
        else:
            print(f"❌ '{query}' 검색 결과가 없습니다.")
            print("💡 다른 키워드를 시도해보세요.")
        
        return len(hits) > 0
        
    except Exception as e:
        print(f"❌ 검색 오류: {e}")
        return False

def show_help():
    """도움말 표시"""
    print("\n" + "="*60)
    print("📘 법령 검색 시스템 v2.0 도움말 (attachment processor)")
    print("="*60)
    print("🔍 검색 명령어:")
    print("  • 일반 검색: 스토킹")
    print("  • 구문 검색: \"스토킹범죄의 처벌 등에 관한 법률\"")
    print("  • 퍼지 검색: 자동 지원 (오타 허용)")
    print("\n💡 특수 명령어:")
    print("  • help, h : 이 도움말")
    print("  • demo, d : 데모 검색 실행")
    print("  • quit, exit, q : 프로그램 종료")
    print("\n⚖️  법령 정보:")
    print("  • 스토킹범죄의 처벌 등에 관한 법률")
    print("  • 형법 관련 조항")
    print("  • 개인정보보호법")
    print("  • 피해자 보호 조항")
    print("="*60)

def run_demo():
    """데모 검색 실행"""
    print("\n🎯 데모 검색을 실행합니다...")
    
    demo_queries = [
        "스토킹",
        "\"형법\"",
        "처벌",
        "피해자"
    ]
    
    for query in demo_queries:
        print(f"\n🔍 데모 검색: {query}")
        search_legal_content(query, max_results=2)
        print("-" * 40)

def main():
    """메인 실행 함수"""
    print_section("법령 검색 시스템 v2.0 (attachment processor)")
    
    try:
        # 1. Elasticsearch 연결 확인
        if not es.ping():
            print("❌ Elasticsearch 연결 실패")
            return
        
        print("✅ Elasticsearch 연결 성공")
        
        # 2. attachment processor 파이프라인 생성
        if not create_attachment_pipeline():
            print("❌ 파이프라인 생성 실패")
            return
        
        # 3. 인덱스 생성
        if not create_legal_index():
            print("❌ 인덱스 생성 실패")
            return
        
        # 4. PDF 문서 인덱싱
        pdf_path = "stalker.pdf"
        if not index_pdf_document(pdf_path):
            print("❌ PDF 인덱싱 실패")
            return
        
        # 5. 인덱싱 결과 확인
        if not verify_indexing():
            print("❌ 인덱싱 확인 실패")
            return
        
        print_section("법령 검색 시스템 준비 완료! 🎉")
        print("💡 'help' 입력시 도움말, 'demo' 입력시 데모 실행")
        
        # 6. 대화형 검색 시작
        while True:
            try:
                query = input("\n🔍 검색어를 입력하세요 (종료: quit): ").strip()
                
                if not query:
                    continue
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 법령 검색 시스템을 종료합니다.")
                    break
                
                if query.lower() in ['help', 'h']:
                    show_help()
                    continue
                
                if query.lower() in ['demo', 'd']:
                    run_demo()
                    continue
                
                # 검색 실행
                search_legal_content(query)
                
            except KeyboardInterrupt:
                print("\n\n👋 법령 검색 시스템을 종료합니다.")
                break
            except Exception as e:
                print(f"❌ 오류 발생: {e}")
    
    except Exception as e:
        print(f"❌ 시스템 오류: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main() 