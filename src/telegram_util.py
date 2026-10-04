import requests
from src.config import TELEGRAM_TOKEN, CHAT_ID

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    response = requests.post(url, json=payload)
    return response

def get_latest_telegram_message(last_update_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    params = {'timeout': 5, 'offset': last_update_id}
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        raise RuntimeError("텔레그램 메시지를 수신하지 못했습니다.") from None
    if not data.get("ok"):
        raise RuntimeError("텔레그램 메시지 수신 요청이 거부되었습니다.")
    return data
