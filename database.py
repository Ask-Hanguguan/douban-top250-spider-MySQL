import pymysql
import time
from config import MYSQL_CONFIG
from logger import setup_logger

logger = setup_logger('database')

class DatabaseManager:
    # SQL语句常量
    INSERT_SQL = """
    INSERT INTO movies (`rank`, title, director, actors, year, region, genre, rating, rating_count, quote, detail_url)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        title = VALUES(title),
        director = VALUES(director),
        actors = VALUES(actors),
        year = VALUES(year),
        region = VALUES(region),
        genre = VALUES(genre),
        rating = VALUES(rating),
        rating_count = VALUES(rating_count),
        quote = VALUES(quote),
        detail_url = VALUES(detail_url)
    """

    def __init__(self):
        self._validate_config()
        self.connection = None
        self.connect()

    def _validate_config(self):
        """验证MySQL配置"""
        required_keys = ['host', 'port', 'user', 'password', 'database', 'charset']
        for key in required_keys:
            if key not in MYSQL_CONFIG:
                raise ValueError(f"MySQL配置缺少必需的键: {key}")

        # 验证端口是否为整数
        try:
            port = int(MYSQL_CONFIG['port'])
            if port <= 0 or port > 65535:
                raise ValueError(f"端口号无效: {port}")
            MYSQL_CONFIG['port'] = port  # 确保端口为整数
        except (ValueError, TypeError):
            raise ValueError(f"端口号必须为整数: {MYSQL_CONFIG['port']}")
    
    def connect(self, max_retries=3, retry_delay=2):
        """连接数据库，支持重试机制"""
        for attempt in range(max_retries):
            try:
                self.connection = pymysql.connect(
                    host=MYSQL_CONFIG['host'],
                    port=MYSQL_CONFIG['port'],
                    user=MYSQL_CONFIG['user'],
                    password=MYSQL_CONFIG['password'],
                    charset=MYSQL_CONFIG['charset'],
                    cursorclass=pymysql.cursors.DictCursor
                )
                logger.info("数据库连接成功")
                self._create_database()
                self._create_table()
                return  # 连接成功，直接返回
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"数据库连接失败，{retry_delay}秒后重试... (尝试 {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"数据库连接失败，已重试{max_retries}次: {e}")
                    raise
    
    def _create_database(self):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_CONFIG['database']} CHARACTER SET {MYSQL_CONFIG['charset']}")
            self.connection.commit()
            logger.info(f"数据库 {MYSQL_CONFIG['database']} 已创建或已存在")
            
            self.connection.select_db(MYSQL_CONFIG['database'])
        except Exception as e:
            logger.error(f"创建数据库失败: {e}")
            raise
    
    def _create_table(self):
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS movies (
            id INT AUTO_INCREMENT PRIMARY KEY,
            `rank` INT NOT NULL UNIQUE,
            title VARCHAR(255) NOT NULL,
            director VARCHAR(500),
            actors TEXT,
            year VARCHAR(50),
            region VARCHAR(255),
            genre VARCHAR(255),
            rating DECIMAL(3,1) NOT NULL,
            rating_count BIGINT NOT NULL,
            quote TEXT,
            detail_url VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_rank (`rank`),
            INDEX idx_rating (rating)
        ) ENGINE=InnoDB DEFAULT CHARSET={MYSQL_CONFIG['charset']}
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(create_table_sql)
            self.connection.commit()
            logger.info("movies表已创建或已存在")
        except Exception as e:
            logger.error(f"创建表失败: {e}")
            raise
    
    def insert_movie(self, movie_data):
        insert_sql = self.INSERT_SQL
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(insert_sql, (
                    movie_data['rank'],
                    movie_data['title'],
                    movie_data['director'],
                    movie_data['actors'],
                    movie_data['year'],
                    movie_data['region'],
                    movie_data['genre'],
                    movie_data['rating'],
                    movie_data['rating_count'],
                    movie_data['quote'],
                    movie_data['detail_url']
                ))
            self.connection.commit()
            logger.debug(f"电影 {movie_data['title']} 插入成功")
        except Exception as e:
            logger.error(f"插入电影失败: {e}")
            self.connection.rollback()
            raise
    
    def batch_insert_movies(self, movies_list):
        """批量插入电影数据，使用事务包裹提高性能"""
        if not movies_list:
            logger.warning("电影列表为空，跳过批量插入")
            return

        insert_sql = self.INSERT_SQL

        try:
            with self.connection.cursor() as cursor:
                # 准备批量数据
                batch_data = []
                for movie in movies_list:
                    batch_data.append((
                        movie['rank'],
                        movie['title'],
                        movie['director'],
                        movie['actors'],
                        movie['year'],
                        movie['region'],
                        movie['genre'],
                        movie['rating'],
                        movie['rating_count'],
                        movie['quote'],
                        movie['detail_url']
                    ))

                # 使用executemany批量执行
                cursor.executemany(insert_sql, batch_data)

            self.connection.commit()
            logger.info(f"批量插入 {len(movies_list)} 部电影完成")
        except Exception as e:
            self.connection.rollback()
            logger.error(f"批量插入电影失败: {e}")
            raise
    
    def get_all_movies(self):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT * FROM movies ORDER BY `rank`")
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"查询电影失败: {e}")
            raise
    
    def close(self):
        if self.connection:
            self.connection.close()
            logger.info("数据库连接已关闭")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
