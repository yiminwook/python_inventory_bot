import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
PURCHASE_PAGE_URL = os.environ.get('PURCHASE_PAGE_URL')
RELATIVE_CHROME_DRIVER_PATH = os.environ.get("CHROME_DRIVER_PATH") # 실제 ChromeDriver의 경로로 변경
ABSOLUTE_CHROME_DRIVER_PATH  = os.path.abspath(RELATIVE_CHROME_DRIVER_PATH)
print("path", ABSOLUTE_CHROME_DRIVER_PATH)