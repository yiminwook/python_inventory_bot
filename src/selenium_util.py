from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from src.config import CHROME_DRIVER_PATH, PURCHASE_PAGE_URL

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

service = Service(CHROME_DRIVER_PATH)
driver = None

def start_chrome_driver():
    global driver
    if driver is None:
        driver = webdriver.Chrome(service=service, options=options)

def stop_chrome_driver():
    global driver
    if driver is not None:
        driver.quit()
        driver = None

def get_page_content():
    start_chrome_driver()
    driver.get(PURCHASE_PAGE_URL)
    add_to_cart_visible = False

    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//body"))
        )
        try:
            add_to_cart_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Add to cart')]"))
            )
            add_to_cart_visible = True
        except TimeoutException:
            add_to_cart_visible = False
    finally:
        stop_chrome_driver()

    return add_to_cart_visible
