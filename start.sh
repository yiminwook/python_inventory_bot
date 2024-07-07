#!/bin/bash

# 스크립트가 위치한 디렉토리로 이동 (프로젝트 루트 디렉토리로 이동)
cd "$(dirname "$0")"

# 가상환경 활성화
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# main.py를 nohup으로 백그라운드에서 실행하고 로그를 output.log에 저장
nohup python3 -u main.py > output.log 2>&1 &