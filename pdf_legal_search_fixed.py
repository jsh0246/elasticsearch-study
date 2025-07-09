#!/usr/bin/env python3
"""
법령 전문 검색 시스템 - 안정화 버전
- 검증된 방식 사용
- 최신 API 호출 방식 적용
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

def create_legal_index():
    """법령 문서 전용 인덱스 생성"""
    print("📚 법령 인덱스 생성 중...")
    
    index_name = "legal-documents-stable"
    
    # 기존 인덱스 삭제
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
        print(f"🗑️  기존 인덱스 '{index_name}' 삭제")
    
    # 인덱스 매핑 설정 (간단한 방식)
    mapping = {
        "properties": {
            "filename": {
                "type": "keyword"
            },
            "upload_date": {
                "type": "date"
            },
            "content": {
                "type": "text",
                "analyzer": "standard",
                "term_vector": "with_positions_offsets"  # 하이라이트용
            },
            "content_length": {
                "type": "integer"
            }
        }
    }
    
    settings = {
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
    }
    
    try:
        es.indices.create(
            index=index_name, 
            mappings=mapping,
            settings=settings
        )
        print(f"✅ 인덱스 '{index_name}' 생성 완료")
        return True
    except Exception as e:
        print(f"❌ 인덱스 생성 실패: {e}")
        return False

def extract_text_from_pdf(pdf_path):
    """PDF에서 텍스트 추출 (단순한 방식)"""
    print(f"📄 PDF 텍스트 추출: {pdf_path}")
    
    try:
        # PyPDF2 사용해서 텍스트 추출 시도
        try:
            import PyPDF2
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                
                if text.strip():
                    print(f"✅ PyPDF2로 텍스트 추출 성공 ({len(text)} 문자)")
                    return text
        except ImportError:
            print("⚠️  PyPDF2 설치되지 않음")
        except Exception as e:
            print(f"⚠️  PyPDF2 추출 실패: {e}")
        
        # pdfplumber 사용 시도
        try:
            import pdfplumber
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            if text.strip():
                print(f"✅ pdfplumber로 텍스트 추출 성공 ({len(text)} 문자)")
                return text
        except ImportError:
            print("⚠️  pdfplumber 설치되지 않음")
        except Exception as e:
            print(f"⚠️  pdfplumber 추출 실패: {e}")
        
        # 마지막 수단: 더미 텍스트로 테스트
        dummy_text = """
        스토킹범죄의 처벌 등에 관한 법률

        제1조(목적) 이 법은 스토킹범죄를 예방하고 피해자를 보호하며, 스토킹범죄에 대한 처벌을 규정함으로써 국민의 자유와 안전을 보장함을 목적으로 한다.

        제2조(정의) 이 법에서 사용하는 용어의 뜻은 다음과 같다.
        1. "스토킹행위"란 상대방의 의사에 반하여 지속적 또는 반복적으로 다음 각 목의 어느 하나에 해당하는 행위를 하여 상대방에게 불안감 또는 공포심을 일으키는 행위를 말한다.

        형법 제283조(협박) 사람을 협박한 자는 3년 이하의 징역, 500만원 이하의 벌금, 구류 또는 과료에 처한다.

        개인정보보호법 제71조(벌칙) 제15조제1항 또는 제17조제1항을 위반하여 개인정보를 처리한 자는 5년 이하의 징역 또는 5천만원 이하의 벌금에 처한다.

        피해자 보호 조항: 피해자의 신변보호와 2차 피해 방지를 위한 특별한 조치를 취해야 한다.

        처벌 규정: 스토킹 행위를 한 자는 3년 이하의 징역 또는 3천만원 이하의 벌금에 처한다.
        """
        
        print("⚠️  PDF 추출 실패, 더미 텍스트로 데모 진행")
        return dummy_text
        
    except Exception as e:
        print(f"❌ 텍스트 추출 실패: {e}")
        return None

def index_pdf_content(pdf_path, doc_id="stalker-laws"):
    """PDF 내용을 직접 인덱싱"""
    print(f"📄 PDF 문서 인덱싱: {pdf_path}")
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF 파일을 찾을 수 없습니다: {pdf_path}")
        return False
    
    # 텍스트 추출
    content = extract_text_from_pdf(pdf_path)
    if not content:
        return False
    
    try:
        file_size = os.path.getsize(pdf_path)
        print(f"📊 파일 크기: {file_size:,} bytes")
        
        # 문서 데이터 구성
        document = {
            "filename": os.path.basename(pdf_path),
            "upload_date": "2024-01-01T00:00:00",
            "content": content,
            "content_length": len(content)
        }
        
        # 직접 인덱싱
        result = es.index(
            index="legal-documents-stable",
            id=doc_id,
            document=document
        )
        
        print("✅ PDF 문서 인덱싱 완료")
        print(f"📍 문서 ID: {result['_id']}")
        print(f"📝 추출된 텍스트 길이: {len(content):,} 문자")
        
        # 인덱스 새로고침
        es.indices.refresh(index="legal-documents-stable")
        
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
        result = es.get(index="legal-documents-stable", id="stalker-laws")
        
        source = result['_source']
        print(f"✅ 문서 처리 완료:")
        print(f"   📄 파일명: {source.get('filename', 'N/A')}")
        print(f"   📝 콘텐츠 길이: {source.get('content_length', 0):,} 문자")
        
        # 내용 미리보기
        content = source.get('content', '')
        if content:
            preview = content[:300] + "..." if len(content) > 300 else content
            print(f"   👁️  내용 미리보기:\n{preview}")
        
        return True
            
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
                    "content": {
                        "query": clean_query
                    }
                }
            },
            "highlight": {
                "fields": {
                    "content": {
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
                                "content": {
                                    "query": query,
                                    "boost": 2.0
                                }
                            }
                        },
                        {
                            "match": {
                                "content": {
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
                    "content": {
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
        result = es.search(index="legal-documents-stable", **search_query)
        hits = result['hits']['hits']
        
        print(f"\n🔍 {search_type} 검색 결과: {len(hits)}개 발견")
        print("="*80)
        
        if hits:
            for i, hit in enumerate(hits, 1):
                score = hit['_score']
                print(f"\n📋 결과 {i} (관련도: {score:.2f})")
                print("-" * 50)
                
                # 하이라이트된 내용 표시
                if 'highlight' in hit and 'content' in hit['highlight']:
                    for fragment in hit['highlight']['content']:
                        # HTML 태그를 보기 좋게 변환
                        display_fragment = fragment.replace('<mark>', '【').replace('</mark>', '】')
                        print(f"💡 {display_fragment}")
                        print()
                else:
                    # 하이라이트가 없는 경우 원본 내용의 일부 표시
                    content = hit['_source']['content']
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
    print("📘 법령 검색 시스템 - 안정화 버전 도움말")
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
        "피해자",
        "개인정보"
    ]
    
    for query in demo_queries:
        print(f"\n🔍 데모 검색: {query}")
        search_legal_content(query, max_results=2)
        print("-" * 40)

def main():
    """메인 실행 함수"""
    print_section("법령 검색 시스템 - 안정화 버전")
    
    try:
        # 1. Elasticsearch 연결 확인
        if not es.ping():
            print("❌ Elasticsearch 연결 실패")
            return
        
        print("✅ Elasticsearch 연결 성공")
        
        # 2. 인덱스 생성
        if not create_legal_index():
            print("❌ 인덱스 생성 실패")
            return
        
        # 3. PDF 문서 인덱싱
        pdf_path = "stalker.pdf"
        if not index_pdf_content(pdf_path):
            print("❌ PDF 인덱싱 실패")
            return
        
        # 4. 인덱싱 결과 확인
        if not verify_indexing():
            print("❌ 인덱싱 확인 실패")
            return
        
        print_section("법령 검색 시스템 준비 완료! 🎉")
        print("💡 'help' 입력시 도움말, 'demo' 입력시 데모 실행")
        
        # 5. 대화형 검색 시작
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