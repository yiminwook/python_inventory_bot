#!/bin/bash

# 스크립트가 위치한 디렉토리로 이동 (프로젝트 루트 디렉토리로 이동)
cd "$(dirname "$0")"

# 가상환경 활성화
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# main.py 실행
python ./main.py