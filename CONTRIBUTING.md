# 🤝 기여 가이드라인

Elasticsearch 실습 프로젝트에 기여해주셔서 감사합니다! 이 문서는 기여 방법을 안내합니다.

## 📋 목차
- [시작하기](#시작하기)
- [개발 환경 설정](#개발-환경-설정)
- [기여 방법](#기여-방법)
- [코딩 스타일](#코딩-스타일)
- [커밋 메시지 규칙](#커밋-메시지-규칙)
- [이슈 및 PR 가이드라인](#이슈-및-pr-가이드라인)

## 🚀 시작하기

### 기여할 수 있는 영역
- 🐛 버그 수정
- ✨ 새로운 검색 기능 추가
- 📚 문서 개선
- 🧪 테스트 추가
- 🎨 코드 품질 개선
- 🌐 다국어 지원

## 💻 개발 환경 설정

### 1. 저장소 포크 및 클론
```bash
# 저장소 포크 후
git clone https://github.com/YOUR_USERNAME/elasticsearch-practice.git
cd elasticsearch-practice/p1
```

### 2. 개발 환경 설정
```bash
# uv를 사용한 의존성 설치
uv sync

# 또는 자동 설치 스크립트 사용
./setup.sh  # Linux/macOS
# 또는
setup.bat   # Windows
```

### 3. Elasticsearch 실행
```bash
docker run --name elasticsearch \
  -p 9200:9200 -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "ELASTIC_PASSWORD=OBIpKj46" \
  -e "xpack.security.enabled=true" \
  docker.elastic.co/elasticsearch/elasticsearch:9.0.3
```

### 4. 기본 테스트 실행
```bash
uv run main.py
```

## 🛠️ 기여 방법

### 1. 브랜치 생성
```bash
git checkout -b feature/your-feature-name
# 또는
git checkout -b fix/bug-description
```

### 2. 변경사항 작성
- 명확하고 간결한 코드 작성
- 적절한 주석 추가
- 관련 문서 업데이트

### 3. 테스트
```bash
# 기본 스크립트 테스트
uv run main.py
uv run simple_utils.py

# 새로운 기능 테스트
uv run your_new_script.py
```

### 4. 커밋 및 푸시
```bash
git add .
git commit -m "feat: 새로운 검색 기능 추가"
git push origin feature/your-feature-name
```

### 5. Pull Request 생성
- 명확한 제목과 설명 작성
- 관련 이슈 번호 참조
- 테스트 완료 확인

## 📝 코딩 스타일

### Python 코딩 스타일
- PEP 8 스타일 가이드 준수
- 함수와 변수명은 snake_case 사용
- 클래스명은 PascalCase 사용
- 적절한 docstring 추가

### 예시
```python
def search_documents(query: str, index_name: str = "default") -> dict:
    """
    Elasticsearch에서 문서를 검색합니다.
    
    Args:
        query (str): 검색 쿼리
        index_name (str): 인덱스 이름
        
    Returns:
        dict: 검색 결과
    """
    # 구현 코드
    pass
```

### 파일 구조
```
p1/
├── main.py                    # 기본 실습
├── advanced_search.py         # 고급 검색
├── korean_search.py          # 한국어 검색
├── pdf_legal_search.py       # 법령 검색
├── utils/                    # 유틸리티 함수들
└── tests/                    # 테스트 파일들
```

## 💬 커밋 메시지 규칙

### 형식
```
<타입>(<범위>): <제목>

<본문>

<푸터>
```

### 타입
- `feat`: 새로운 기능
- `fix`: 버그 수정
- `docs`: 문서 수정
- `style`: 코드 포맷팅
- `refactor`: 코드 리팩토링
- `test`: 테스트 추가
- `chore`: 빌드/설정 변경

### 예시
```
feat(search): 퍼지 검색 기능 추가

사용자가 오타가 있는 검색어로도 결과를 찾을 수 있도록
Elasticsearch의 fuzzy 쿼리를 구현했습니다.

Closes #123
```

## 📋 이슈 및 PR 가이드라인

### 이슈 작성
1. 🐛 **버그 리포트**: 명확한 재현 단계와 환경 정보 포함
2. ✨ **기능 요청**: 구체적인 사용 사례와 예상 동작 설명
3. 📚 **문서 개선**: 개선이 필요한 부분과 제안사항 명시

### Pull Request 작성
1. **명확한 제목**: 변경사항을 한 줄로 요약
2. **상세한 설명**: 변경 이유와 방법 설명
3. **테스트 확인**: 모든 관련 기능 테스트 완료
4. **문서 업데이트**: README나 주석 업데이트 포함

## 🔍 코드 리뷰 프로세스

### 리뷰 기준
- ✅ 코드가 의도한 대로 작동하는가?
- ✅ 코드가 읽기 쉽고 유지보수 가능한가?
- ✅ 적절한 에러 처리가 되어 있는가?
- ✅ 성능에 부정적인 영향이 없는가?
- ✅ 문서가 적절히 업데이트되었는가?

### 리뷰 응답
- 피드백에 대해 정중하게 응답
- 필요한 경우 추가 설명 제공
- 제안된 변경사항 적극적으로 검토

## 🆘 도움이 필요한 경우

### 질문하기
- 💬 **Discussion**: 일반적인 질문이나 아이디어 공유
- 🐛 **Issue**: 구체적인 문제 신고
- 📧 **이메일**: 개인적인 문의 사항

### 리소스
- [Elasticsearch 공식 문서](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [Python Elasticsearch 클라이언트](https://elasticsearch-py.readthedocs.io/)
- [uv 패키지 매니저](https://docs.astral.sh/uv/)

## 🙏 감사 인사

모든 기여자분들께 감사드립니다! 여러분의 기여가 이 프로젝트를 더욱 발전시킵니다.

---

궁금한 점이 있으시면 언제든 이슈를 열어주세요! 🚀 