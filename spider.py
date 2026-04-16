import requests
import time
from bs4 import BeautifulSoup
from config import DOUBAN_BASE_URL, REQUEST_HEADERS, REQUEST_INTERVAL
from logger import setup_logger

logger = setup_logger('spider')

class DoubanSpider:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(REQUEST_HEADERS)
    
    def get_page(self, url):
        try:
            logger.info(f"正在请求: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'
            time.sleep(REQUEST_INTERVAL)
            return response.text
        except requests.RequestException as e:
            logger.error(f"请求失败: {url}, 错误: {e}")
            raise
    
    def parse_movie_item(self, item):
        movie = {
            'rank': 0,
            'title': '',
            'director': '',
            'actors': '',
            'year': '',
            'region': '',
            'genre': '',
            'rating': 0.0,
            'rating_count': 0,
            'quote': '',
            'detail_url': ''
        }
        
        rank_elem = item.find('em')
        movie['rank'] = int(rank_elem.get_text()) if rank_elem else 0
        
        title_elem = item.find('span', class_='title')
        movie['title'] = title_elem.get_text() if title_elem else ''
        
        detail_url_elem = item.find('a')
        movie['detail_url'] = detail_url_elem['href'] if detail_url_elem and 'href' in detail_url_elem.attrs else ''
        
        info_elem = item.find('div', class_='bd').find('p')
        info_text = info_elem.get_text(separator='\n', strip=True) if info_elem else ''
        
        lines = info_text.split('\n')
        if len(lines) >= 1:
            director_part = lines[0].strip()
            if '导演:' in director_part:
                movie['director'] = director_part.split('导演:')[-1].split('主演:')[0].strip()
            else:
                movie['director'] = ''
            
            if '主演:' in director_part:
                movie['actors'] = director_part.split('主演:')[-1].strip()
            else:
                movie['actors'] = ''
        
        if len(lines) >= 2:
            year_part = lines[1].strip()
            parts = year_part.split('/')
            if len(parts) >= 1:
                movie['year'] = parts[0].strip()
            if len(parts) >= 2:
                movie['region'] = parts[1].strip()
            if len(parts) >= 3:
                movie['genre'] = parts[2].strip()
        
        rating_elem = item.find('span', class_='rating_num')
        movie['rating'] = float(rating_elem.get_text()) if rating_elem else 0.0
        
        rating_count_elem = item.find('div', class_='star').find_all('span')[-1] if item.find('div', class_='star') else None
        if rating_count_elem:
            count_text = rating_count_elem.get_text()
            movie['rating_count'] = int(count_text.replace('人评价', ''))
        else:
            movie['rating_count'] = 0
        
        quote_elem = item.find('span', class_='inq')
        movie['quote'] = quote_elem.get_text() if quote_elem else ''
        
        return movie
    
    def parse_page(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        movie_items = soup.find_all('div', class_='item')
        
        movies = []
        for item in movie_items:
            try:
                movie = self.parse_movie_item(item)
                movies.append(movie)
                logger.debug(f"解析电影: {movie['title']}")
            except Exception as e:
                logger.error(f"解析电影失败: {e}")
        
        return movies
    
    def crawl(self):
        all_movies = []
        
        for start in range(0, 250, 25):
            url = f"{DOUBAN_BASE_URL}?start={start}"
            try:
                html = self.get_page(url)
                movies = self.parse_page(html)
                all_movies.extend(movies)
                logger.info(f"第 {start//25 + 1} 页爬取完成，获取 {len(movies)} 部电影")
            except Exception as e:
                logger.error(f"爬取第 {start//25 + 1} 页失败: {e}")
                continue
        
        logger.info(f"爬取完成，共获取 {len(all_movies)} 部电影")
        return all_movies
