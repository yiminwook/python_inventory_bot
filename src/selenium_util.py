from selenium import webdriver
import threading
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from src.config import ABSOLUTE_CHROME_DRIVER_PATH, PURCHASE_PAGE_URL
from src.util import time_print

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service(ABSOLUTE_CHROME_DRIVER_PATH)
driver = None
shutdown_requested = threading.Event()

def request_browser_shutdown():
    shutdown_requested.set()

def start_chrome_driver():
    global driver
    if shutdown_requested.is_set():
        raise RuntimeError("프로그램 종료 중입니다.")
    if driver is None:
        driver = webdriver.Chrome(service=service, options=options)
        if shutdown_requested.is_set():
            stop_chrome_driver()
            raise RuntimeError("프로그램 종료 중입니다.")
        driver.set_page_load_timeout(45)

def stop_chrome_driver():
    global driver
    if driver is not None:
        current_driver = driver
        driver = None
        try:
            current_driver.quit()
        except Exception as e:
            time_print(f"브라우저 종료 실패: {e}")

def get_page_content():
    """Return True/False for button visibility, or None if the check failed."""
    add_to_cart_visible = None

    try:
        start_chrome_driver()
        if shutdown_requested.is_set():
            return None
        driver.get(PURCHASE_PAGE_URL)
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//body"))
        )
        try:
            # Match text inside nested spans and require a visible button.
            WebDriverWait(driver, 5).until(
                EC.visibility_of_any_elements_located((
                    By.XPATH,
                    "//button[contains(normalize-space(.), 'カートに入れる')]",
                ))
            )
            add_to_cart_visible = True
            time_print("Found 'Add to cart' button")
        except TimeoutException:
            time_print("장바구니 버튼이 보이지 않습니다.")
            add_to_cart_visible = False
    except TimeoutException as e:
        time_print(f"페이지 로딩 시간 초과. 다음 주기에 다시 확인합니다: {e}")
    except Exception as e:
        time_print(f"재고 확인 실패. 다음 주기에 다시 확인합니다: {e}")
    finally:
        stop_chrome_driver()

    return add_to_cart_visible
