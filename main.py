import sys
import time
import threading

from src.config import PURCHASE_PAGE_URL, CHAT_ID
from src.util import time_print
from src.telegram_util import send_telegram_message, get_latest_telegram_message
from src.selenium_util import get_page_content

alert_active = False
last_update_id = None
terminate_program = False
add_to_cart_visible = False
alert_thread = None

def initialize_last_update_id():
    global last_update_id
    data = get_latest_telegram_message(last_update_id)
    print(data)
    if data["result"]:
        last_update_id = data["result"][-1]["update_id"] + 1
    else:
        last_update_id = None
    send_telegram_message("모니터링 서버 시작합니다. " + PURCHASE_PAGE_URL)

def alert_until_acknowledged():
    global alert_active, terminate_program, last_update_id
    next_alert_at = time.monotonic() + 8
    while alert_active and not terminate_program:
        try:
            data = get_latest_telegram_message(last_update_id)
        except (RuntimeError, ValueError):
            time_print("텔레그램 메시지 수신 실패. 다시 시도합니다.")
            time.sleep(1)
            continue
        for update in data.get("result", []):
            last_update_id = update["update_id"] + 1
            message = update.get("message", {})
            if str(message.get("chat", {}).get("id")) != str(CHAT_ID):
                continue
            text = message.get("text", "")
            if "확인함" in "".join(text.split()):
                alert_active = False
                terminate_program = True
                time_print("확인하였습니다. 알람을 멈춥니다.")
                send_telegram_message("확인하였습니다. 프로그램을 종료합니다.")
                return

        if not alert_active or terminate_program:
            return
        if time.monotonic() >= next_alert_at:
            time_print("재고 떴어! 접속해! in alert_until_acknowledged")
            send_telegram_message("재고 떴어! 접속해! '확인함'을 입력하면 알람이 멈춥니다.")
            send_telegram_message(PURCHASE_PAGE_URL)
            next_alert_at = time.monotonic() + 8

        time.sleep(1)

def start_alert_thread():
    global alert_thread
    if alert_thread is None or not alert_thread.is_alive():
        alert_thread = threading.Thread(target=alert_until_acknowledged)
        alert_thread.start()

def monitor_browser():
    global add_to_cart_visible, alert_active
    time_print("60초에 1회씩 check_for_page_change")
    initialize_last_update_id()

    while not terminate_program:
        new_add_to_cart_visible = get_page_content()
        time_print(f"--재고 확인 끝-- : {alert_active}")

        if new_add_to_cart_visible != add_to_cart_visible:
            if new_add_to_cart_visible:
                alert_active = True
                time_print("get_page_content, 재고뜸!!!")
                send_telegram_message("재고떴어!! 접속해!!")
                send_telegram_message(PURCHASE_PAGE_URL)
            else:
                alert_active = False
            add_to_cart_visible = new_add_to_cart_visible
        if alert_active:
            start_alert_thread()
        time.sleep(60)

time_print("모니터링 시작")

if __name__ == "__main__":
    print("monitoring_thread 시작")
    monitoring_thread = threading.Thread(target=monitor_browser)
    monitoring_thread.daemon = True
    monitoring_thread.start()

    while not terminate_program:
        time.sleep(1)

    time_print("프로그램 종료 중...")
    sys.exit(0)
