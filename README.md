## 로컬 환경설정

python --version 3.12.4

```
python3 -m venv .venv

pip install -r requirements
```

## 실행

```
# 권한없을때
chmod 755 ./start.sh

./start.sh
```

## 백그라운드 실행

```
nohup ./start.sh &
```

## 백그라운드 프로세스 종료

```
ps -ef | grep main.py
sudo kill -9 {PID}
```

## 가상환경 종료

```
deactivate
```
