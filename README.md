## 로컬 환경설정

python --version 3.12.4

```
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

sudo dpkg -i google-chrome-stable_current_amd64.deb

# 의존성 에러 발생시
sudo apt --fix-broken install

google-chrome --version
```

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
nohup python3 -u main.py > output.log 2>&1 &
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
