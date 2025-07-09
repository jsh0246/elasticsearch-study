from elasticsearch import Elasticsearch
import base64
import os
import json
import traceback
from pathlib import Path

# Elasticsearch 연결 설정
es = Elasticsearch(
    "http://localhost:9200",
    basic_auth=("elastic", "OBIpKj46")
)

def print_section(title):
    print("\n" + "="*60)
    print(f"📚 {title}")
    print("="*60)

def check_attachment_plugin():
    """Elasticsearch attachment 플러그인 설치 확인"""
    try:
        plugins = es.cat.plugins(format="json")
        attachment_installed = any(plugin.get('component') == 'ingest-attachment' for plugin in plugins)
        return attachment_installed
    except Exception as e:
        print(f"플러그인 확인 중 오류: {e}")
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

def create_attachment_pipeline():
    """PDF 첨부파일 처리 파이프라인 생성"""
    pipeline = {
        "description": "PDF 파일 텍스트 추출을 위한 파이프라인",
        "processors": [
            {
                "attachment": {
                    "field": "data",
                    "target_field": "attachment",
                    "indexed_chars": -1  # 모든 문자 인덱싱
                }
            },
            {
                "remove": {
                    "field": "data"  # 원본 바이너리 데이터 제거 (공간 절약)
                }
            }
        ]
    }
    
    es.ingest.put_pipeline(id="attachment", body=pipeline)
    print("✅ Attachment 파이프라인 생성 완료")

def create_pdf_index():
    """PDF 문서 저장을 위한 인덱스 생성"""
    index_name = "pdf_documents"
    
    # 기존 인덱스 삭제
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
        print(f"🗑️ 기존 인덱스 '{index_name}' 삭제")
    
    # 매핑 설정
    mapping = {
        "mappings": {
            "properties": {
                "filename": {
                    "type": "keyword"
                },
                "upload_date": {
                    "type": "date"
                },
                "file_size": {
                    "type": "long"
                },
                "attachment": {
                    "properties": {
                        "content": {
                            "type": "text",
                            "analyzer": "standard"
                        },
                        "title": {
                            "type": "text"
                        },
                        "author": {
                            "type": "keyword"
                        },
                        "content_type": {
                            "type": "keyword"
                        },
                        "content_length": {
                            "type": "long"
                        }
                    }
                }
            }
        }
    }
    
    es.indices.create(index=index_name, body=mapping)
    print(f"✅ 인덱스 '{index_name}' 생성 완료")
    return index_name

def create_sample_pdf():
    """테스트용 간단한 PDF 생성"""
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        
        print("📄 샘플 PDF 생성 중...")
        
        # 폰트 등록 (한글 지원)
        try:
            # 시스템 폰트 사용 시도
            pdfmetrics.registerFont(TTFont('NanumGothic', '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'))
            font_name = 'NanumGothic'
        except:
            # 기본 폰트 사용
            font_name = 'Helvetica'
        
        # PDF 파일들 생성
        pdfs = [
            {
                "filename": "elasticsearch_guide.pdf",
                "content": [
                    "Elasticsearch 완전 가이드",
                    "",
                    "Elasticsearch는 분산 검색 및 분석 엔진입니다.",
                    "실시간 검색, 로그 분석, 비즈니스 인텔리전스에 사용됩니다.",
                    "",
                    "주요 기능:",
                    "- 전문 검색 (Full-text search)",
                    "- 집계 분석 (Aggregations)",
                    "- 실시간 인덱싱",
                    "- 분산 아키텍처",
                    "",
                    "이 문서는 Elasticsearch 학습을 위한 샘플 PDF입니다."
                ]
            },
            {
                "filename": "python_tutorial.pdf", 
                "content": [
                    "Python 프로그래밍 튜토리얼",
                    "",
                    "Python은 간단하고 강력한 프로그래밍 언어입니다.",
                    "데이터 분석, 웹 개발, 인공지능 개발에 널리 사용됩니다.",
                    "",
                    "Python의 특징:",
                    "- 읽기 쉬운 문법",
                    "- 풍부한 라이브러리",
                    "- 크로스 플랫폼 지원",
                    "- 강력한 커뮤니티",
                    "",
                    "elasticsearch-py 라이브러리로 Elasticsearch를 사용할 수 있습니다."
                ]
            },
            {
                "filename": "data_science.pdf",
                "content": [
                    "데이터 사이언스 입문",
                    "",
                    "데이터 사이언스는 데이터로부터 인사이트를 추출하는 학문입니다.",
                    "통계학, 머신러닝, 프로그래밍을 결합합니다.",
                    "",
                    "주요 단계:",
                    "1. 데이터 수집",
                    "2. 데이터 전처리",
                    "3. 탐색적 데이터 분석",
                    "4. 모델링",
                    "5. 결과 해석",
                    "",
                    "Elasticsearch는 대용량 데이터 검색과 분석에 유용합니다."
                ]
            }
        ]
        
        for pdf_info in pdfs:
            c = canvas.Canvas(pdf_info["filename"], pagesize=letter)
            width, height = letter
            
            y = height - 50
            for line in pdf_info["content"]:
                if font_name == 'NanumGothic':
                    c.setFont(font_name, 12)
                else:
                    c.setFont("Helvetica", 12)
                c.drawString(50, y, line)
                y -= 20
                if y < 50:  # 페이지 끝에 도달하면 새 페이지
                    c.showPage()
                    y = height - 50
            
            c.save()
            print(f"  ✅ {pdf_info['filename']} 생성 완료")
        
        return [pdf["filename"] for pdf in pdfs]
        
    except ImportError:
        print("⚠️ reportlab 라이브러리가 없어 샘플 PDF를 생성할 수 없습니다.")
        print("pip install reportlab 로 설치하거나, 직접 PDF 파일을 준비해주세요.")
        return []

def index_pdf_file(filename, index_name):
    """PDF 파일을 Elasticsearch에 인덱싱"""
    try:
        if not os.path.exists(filename):
            print(f"❌ 파일을 찾을 수 없습니다: {filename}")
            return False
        
        # PDF 파일을 base64로 인코딩
        with open(filename, "rb") as f:
            pdf_data = base64.b64encode(f.read()).decode('utf-8')
        
        # 파일 정보
        file_size = os.path.getsize(filename)
        
        # 문서 생성
        doc = {
            "filename": filename,
            "upload_date": "2024-01-01T00:00:00",
            "file_size": file_size,
            "data": pdf_data
        }
        
        # 파이프라인을 사용하여 인덱싱
        result = es.index(
            index=index_name,
            body=doc,
            pipeline="attachment"
        )
        
        print(f"✅ PDF 인덱싱 완료: {filename} (ID: {result['_id']})")
        return True
        
    except Exception as e:
        print(f"❌ PDF 인덱싱 실패 - {filename}: {e}")
        return False

def search_pdf_content(query, index_name):
    """PDF 내용에서 키워드 검색"""
    search_body = {
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
                            "attachment.title": {
                                "query": query,
                                "boost": 1.5
                            }
                        }
                    },
                    {
                        "match": {
                            "filename": {
                                "query": query,
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
                    "fragment_size": 150,
                    "number_of_fragments": 3
                }
            }
        },
        "_source": ["filename", "file_size", "upload_date"]
    }
    
    try:
        result = es.search(index=index_name, body=search_body)
        return result
    except Exception as e:
        print(f"❌ 검색 실패: {e}")
        return None

def advanced_pdf_search(index_name):
    """고급 PDF 검색 기능 데모"""
    print_section("🔍 고급 PDF 검색 데모")
    
    search_queries = [
        "Elasticsearch",
        "Python",
        "데이터",
        "분석",
        "프로그래밍"
    ]
    
    for query in search_queries:
        print(f"\n🔎 검색어: '{query}'")
        result = search_pdf_content(query, index_name)
        
        if result and result['hits']['total']['value'] > 0:
            print(f"📊 검색 결과: {result['hits']['total']['value']}개 문서")
            
            for hit in result['hits']['hits']:
                print(f"\n📄 파일: {hit['_source']['filename']}")
                print(f"📏 크기: {hit['_source']['file_size']:,} bytes")
                print(f"⭐ 점수: {hit['_score']:.2f}")
                
                # 하이라이트 표시
                if 'highlight' in hit:
                    print("💡 일치하는 내용:")
                    for fragment in hit['highlight'].get('attachment.content', []):
                        print(f"   {fragment}")
        else:
            print("📭 검색 결과가 없습니다.")
        
        print("-" * 50)

def get_pdf_content(doc_id, index_name):
    """특정 PDF의 전체 내용 조회"""
    try:
        result = es.get(index=index_name, id=doc_id)
        content = result['_source'].get('attachment', {}).get('content', '')
        return content
    except Exception as e:
        print(f"❌ 문서 조회 실패: {e}")
        return None

def main():
    try:
        print_section("📎 Elasticsearch PDF 검색 실습")
        
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
        
        # 3. 파이프라인 생성
        print_section("⚙️ Attachment 파이프라인 설정")
        create_attachment_pipeline()
        
        # 4. 인덱스 생성
        print_section("📁 PDF 인덱스 생성")
        index_name = create_pdf_index()
        
        # 5. 샘플 PDF 생성
        print_section("📄 샘플 PDF 생성")
        pdf_files = create_sample_pdf()
        
        if not pdf_files:
            print("📂 현재 디렉토리의 PDF 파일을 검색합니다...")
            pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
            if not pdf_files:
                print("❌ PDF 파일이 없습니다. 샘플 PDF 생성을 위해 reportlab을 설치하거나 PDF 파일을 추가해주세요.")
                return
        
        # 6. PDF 파일 인덱싱
        print_section("📥 PDF 파일 인덱싱")
        success_count = 0
        for pdf_file in pdf_files:
            if index_pdf_file(pdf_file, index_name):
                success_count += 1
        
        if success_count == 0:
            print("❌ 인덱싱된 PDF가 없습니다.")
            return
        
        # 인덱스 새로고침
        es.indices.refresh(index=index_name)
        print(f"🔄 인덱스 새로고침 완료 ({success_count}개 파일)")
        
        # 7. 검색 테스트
        advanced_pdf_search(index_name)
        
        # 8. 대화형 검색
        print_section("🎯 대화형 PDF 검색")
        print("키워드를 입력하여 PDF를 검색해보세요! (종료: 'quit')")
        
        while True:
            query = input("\n🔍 검색어: ").strip()
            if query.lower() in ['quit', 'exit', '종료']:
                break
            
            if not query:
                continue
            
            result = search_pdf_content(query, index_name)
            if result and result['hits']['total']['value'] > 0:
                print(f"\n📊 '{query}' 검색 결과: {result['hits']['total']['value']}개")
                
                for i, hit in enumerate(result['hits']['hits'][:3], 1):
                    print(f"\n{i}. 📄 {hit['_source']['filename']}")
                    print(f"   ⭐ 점수: {hit['_score']:.2f}")
                    
                    if 'highlight' in hit:
                        for fragment in hit['highlight'].get('attachment.content', [])[:2]:
                            print(f"   💡 {fragment}")
            else:
                print(f"📭 '{query}'에 대한 검색 결과가 없습니다.")
        
        print_section("✅ PDF 검색 실습 완료!")
        print("🎉 씹고수님, PDF 검색 마스터가 되셨네요!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        print("상세 오류 정보:")
        traceback.print_exc()

if __name__ == "__main__":
    main() 