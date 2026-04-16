import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MYSQL_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_DATABASE', 'douban_movies'),
    'charset': os.getenv('DB_CHARSET', 'utf8mb4')
}

DOUBAN_BASE_URL = 'https://movie.douban.com/top250'

REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Connection': 'keep-alive'
}

REQUEST_INTERVAL = 2

LOG_DIR = os.path.join(BASE_DIR, 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'douban_spider.log')

DATA_DIR = os.path.join(BASE_DIR, 'data')
