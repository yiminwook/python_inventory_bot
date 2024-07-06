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
    response = requests.get(url, params=params)
    data = response.json()
    return data