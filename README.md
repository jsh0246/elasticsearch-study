# Elasticsearch 실습 프로젝트

Elasticsearch를 활용한 검색 엔진 학습을 위한 Python 실습 프로젝트입니다.

## 📚 프로젝트 구성

- `main.py` - Elasticsearch 기본 기능 실습 (10단계)
- `advanced_search.py` - 고급 검색 기능 (부분 검색, 퍼지 검색, 와일드카드 등)
- `korean_search.py` - 한국어 검색 최적화
- `bulk_operations.py` - 벌크 인덱싱과 대용량 데이터 처리
- `real_world_search.py` - 실제 검색 서비스 시뮬레이션
- `pdf_search.py` - PDF 파일 첨부파일 검색 (attachment 플러그인)
- `pdf_legal_search.py` - 법령 PDF 전문 검색 시스템 (stalker.pdf 특화)
- `simple_utils.py` - 간단한 유틸리티 함수들
- `elasticsearch_utils.py` - 고급 클러스터 관리 도구

## 🚀 빠른 시작

### 🎯 원클릭 설치 (추천!)

**Linux/macOS:**
```bash
# 프로젝트 폴더로 이동 후 한 번에 설치!
cd p1
./setup.sh
```

**Windows:**
```cmd
# 프로젝트 폴더로 이동 후 한 번에 설치!
cd p1
setup.bat
```

### 📋 수동 설치

#### 1. 프로젝트 클론 및 환경 설정

```bash
# 프로젝트 폴더로 이동
cd p1

# uv를 사용하여 의존성 설치 (한 번에 완료!)
uv sync
```

#### 2. Elasticsearch 실행

Docker를 사용하여 Elasticsearch를 실행합니다:

```bash
# Elasticsearch 컨테이너 실행
docker run --name elasticsearch \
  -p 9200:9200 \
  -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "ELASTIC_PASSWORD=OBIpKj46" \
  -e "xpack.security.enabled=true" \
  docker.elastic.co/elasticsearch/elasticsearch:9.0.3
```

#### 3. 실습 실행

```bash
# 기본 실습 (추천!)
uv run main.py

# 고급 검색 실습
uv run advanced_search.py

# 한국어 검색 실습
uv run korean_search.py

# 벌크 데이터 처리 실습
uv run bulk_operations.py

# 실제 검색 서비스 시뮬레이션
uv run real_world_search.py

# PDF 파일 검색 (고급!)
uv run pdf_search.py

# 법령 PDF 전문 검색 (Ctrl+F 스타일)
uv run pdf_legal_search.py

# 간단한 유틸리티
uv run simple_utils.py

# 클러스터 관리 도구
uv run elasticsearch_utils.py
```

## 🔧 시스템 요구사항

- Python 3.12 이상
- uv (Python 패키지 매니저)
- Docker (Elasticsearch 실행용)
- 최소 2GB RAM

## 📋 학습 내용

### 기본 실습 (main.py)
1. ✅ Elasticsearch 연결 확인
2. 📁 인덱스 생성 및 매핑 설정
3. 📄 문서 추가 (Indexing)
4. 🔍 문서 조회 및 검색
5. 📊 집계 (Aggregations)
6. ✏️ 문서 업데이트
7. 🔧 복합 쿼리

### 법령 검색 시스템 (pdf_legal_search.py)
⚖️ **stalker.pdf 전문 검색**
- 🔍 키워드 검색: `스토킹`, `처벌`, `신고` 등
- 📝 정확한 구문: `"스토킹범죄의 정의"`
- 💡 Ctrl+F 스타일: 즉석 키워드 하이라이트
- 📊 법령 특화: 조문, 항목별 정확한 매칭
- 🎯 대화형 검색: 실시간 법령 조회

### 고급 기능
- **부분 텍스트 검색**: 제목이나 내용의 일부만으로 검색
- **퍼지 검색**: 오타가 있어도 유사한 결과 찾기
- **와일드카드 검색**: `*`과 `?` 문자 활용
- **한국어 최적화**: 한글 텍스트 분석 및 검색
- **PDF 파일 검색**: attachment 플러그인으로 PDF 내용 검색
- **법령 전문 검색**: Ctrl+F 스타일의 정확한 법령 키워드 검색
- **벌크 인덱싱**: 대량 데이터 효율적 처리
- **집계 분석**: 통계 및 그룹화 기능

## 🌐 Elasticsearch 연결 정보

- **URL**: `http://localhost:9200`
- **사용자명**: `elastic`
- **비밀번호**: `OBIpKj46`
- **클러스터명**: `docker-cluster`

## 🛠️ 문제 해결

### 연결 오류 시
1. Elasticsearch 컨테이너가 실행 중인지 확인
2. 포트 9200이 사용 가능한지 확인
3. 방화벽 설정 확인

### 의존성 오류 시
```bash
# 가상환경 재생성
uv sync --reinstall
```

## 📝 추가 학습 자료

- [Elasticsearch 공식 문서](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [Python Elasticsearch 클라이언트](https://elasticsearch-py.readthedocs.io/)
- [uv 사용법](https://docs.astral.sh/uv/)

## 🤝 기여하기

이 프로젝트는 학습 목적으로 만들어졌습니다. 개선 사항이나 새로운 실습 예제가 있다면 언제든 기여해주세요!
