@echo off
chcp 65001 > nul
echo 🚀 Elasticsearch 실습 환경 설정을 시작합니다...

REM 1. uv 설치 확인
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ uv가 설치되어 있지 않습니다.
    echo 📥 uv 설치 중...
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    echo ✅ uv 설치 완료! 새 터미널을 열어서 다시 실행해주세요.
    pause
    exit /b
) else (
    echo ✅ uv가 이미 설치되어 있습니다.
)

REM 2. Python 의존성 설치
echo 📦 Python 의존성 설치 중...
uv sync

REM 3. Docker 설치 확인
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo ⚠️ Docker가 설치되어 있지 않습니다.
    echo 📖 Docker Desktop 설치: https://www.docker.com/products/docker-desktop/
    echo Docker Desktop을 설치한 후 다시 실행해주세요.
    pause
    exit /b
) else (
    echo ✅ Docker가 설치되어 있습니다.
)

REM 4. Elasticsearch 컨테이너 확인 및 실행
docker ps -a --format "table {{.Names}}" | findstr /C:"elasticsearch" >nul
if %errorlevel% equ 0 (
    echo 📊 기존 Elasticsearch 컨테이너를 발견했습니다.
    
    docker ps --format "table {{.Names}}" | findstr /C:"elasticsearch" >nul
    if %errorlevel% equ 0 (
        echo ✅ Elasticsearch가 이미 실행 중입니다.
    ) else (
        echo 🔄 Elasticsearch 컨테이너를 시작합니다...
        docker start elasticsearch
        echo ✅ Elasticsearch 시작 완료!
    )
) else (
    echo 🐳 새로운 Elasticsearch 컨테이너를 생성합니다...
    docker run -d --name elasticsearch ^
        -p 9200:9200 ^
        -p 9300:9300 ^
        -e "discovery.type=single-node" ^
        -e "ELASTIC_PASSWORD=OBIpKj46" ^
        -e "xpack.security.enabled=true" ^
        docker.elastic.co/elasticsearch/elasticsearch:9.0.3
    
    echo ⏳ Elasticsearch 시작을 기다리는 중...
    timeout /t 30 /nobreak >nul
    echo ✅ Elasticsearch 생성 및 시작 완료!
)

REM 5. 연결 테스트
echo 🔍 Elasticsearch 연결 테스트 중...
timeout /t 5 /nobreak >nul

curl -s -u elastic:OBIpKj46 http://localhost:9200 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Elasticsearch 연결 성공!
    echo.
    echo 🎉 환경 설정이 완료되었습니다!
    echo.
    echo 📚 다음 명령어로 실습을 시작하세요:
    echo    uv run main.py              # 기본 실습
    echo    uv run advanced_search.py   # 고급 검색
    echo    uv run korean_search.py     # 한국어 검색
    echo    uv run bulk_operations.py   # 벌크 처리
    echo.
) else (
    echo ❌ Elasticsearch 연결에 실패했습니다.
    echo 🔧 문제 해결:
    echo    1. Docker Desktop이 실행 중인지 확인
    echo    2. 포트 9200이 사용 가능한지 확인
    echo    3. 잠시 후 다시 시도
)

pause 