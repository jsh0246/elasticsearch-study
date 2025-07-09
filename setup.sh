#!/bin/bash

# Elasticsearch 실습 환경 자동 설정 스크립트

echo "🚀 Elasticsearch 실습 환경 설정을 시작합니다..."

# 1. uv 설치 확인
if ! command -v uv &> /dev/null; then
    echo "❌ uv가 설치되어 있지 않습니다."
    echo "📥 uv 설치 중..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.bashrc || source ~/.zshrc
    echo "✅ uv 설치 완료!"
else
    echo "✅ uv가 이미 설치되어 있습니다."
fi

# 2. Python 의존성 설치
echo "📦 Python 의존성 설치 중..."
uv sync

# 3. Docker 설치 확인
if ! command -v docker &> /dev/null; then
    echo "⚠️ Docker가 설치되어 있지 않습니다."
    echo "📖 Docker 설치 가이드: https://docs.docker.com/get-docker/"
    echo "Docker를 설치한 후 다시 실행해주세요."
    exit 1
else
    echo "✅ Docker가 설치되어 있습니다."
fi

# 4. Elasticsearch 컨테이너 확인 및 실행
if docker ps -a --format 'table {{.Names}}' | grep -q '^elasticsearch$'; then
    echo "📊 기존 Elasticsearch 컨테이너를 발견했습니다."
    
    if docker ps --format 'table {{.Names}}' | grep -q '^elasticsearch$'; then
        echo "✅ Elasticsearch가 이미 실행 중입니다."
    else
        echo "🔄 Elasticsearch 컨테이너를 시작합니다..."
        docker start elasticsearch
        echo "✅ Elasticsearch 시작 완료!"
    fi
else
    echo "🐳 새로운 Elasticsearch 컨테이너를 생성합니다..."
    docker run -d \
        --name elasticsearch \
        -p 9200:9200 \
        -p 9300:9300 \
        -e "discovery.type=single-node" \
        -e "ELASTIC_PASSWORD=OBIpKj46" \
        -e "xpack.security.enabled=true" \
        docker.elastic.co/elasticsearch/elasticsearch:9.0.3
    
    echo "⏳ Elasticsearch 시작을 기다리는 중..."
    sleep 30
    echo "✅ Elasticsearch 생성 및 시작 완료!"
fi

# 5. 연결 테스트
echo "🔍 Elasticsearch 연결 테스트 중..."
sleep 5

if curl -s -u elastic:OBIpKj46 http://localhost:9200 > /dev/null; then
    echo "✅ Elasticsearch 연결 성공!"
    echo ""
    echo "🎉 환경 설정이 완료되었습니다!"
    echo ""
    echo "📚 다음 명령어로 실습을 시작하세요:"
    echo "   uv run main.py              # 기본 실습"
    echo "   uv run advanced_search.py   # 고급 검색"
    echo "   uv run korean_search.py     # 한국어 검색"
    echo "   uv run bulk_operations.py   # 벌크 처리"
    echo ""
else
    echo "❌ Elasticsearch 연결에 실패했습니다."
    echo "🔧 문제 해결:"
    echo "   1. Docker 서비스가 실행 중인지 확인"
    echo "   2. 포트 9200이 사용 가능한지 확인"
    echo "   3. 잠시 후 다시 시도"
fi 