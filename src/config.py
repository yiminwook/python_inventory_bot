import os
from dotenv import load_dotenv

load_dotenv()


TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
PURCHASE_PAGE_URL = os.environ.get('PURCHASE_PAGE_URL')
CHROME_DRIVER_PATH = './chromedriver'  # 실제 ChromeDriver의 경로로 변경