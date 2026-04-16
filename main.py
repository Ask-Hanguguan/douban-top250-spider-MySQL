from spider import DoubanSpider
from database import DatabaseManager
from logger import setup_logger

logger = setup_logger('main')

def main():
    logger.info("=" * 50)
    logger.info("豆瓣电影Top250爬虫启动")
    logger.info("=" * 50)
    
    try:
        spider = DoubanSpider()
        movies = spider.crawl()
        
        if movies:
            logger.info(f"准备将 {len(movies)} 部电影存入数据库")
            
            with DatabaseManager() as db:
                db.batch_insert_movies(movies)
                saved_movies = db.get_all_movies()
                logger.info(f"数据库中现有 {len(saved_movies)} 部电影")
                
                logger.info("\nTop10 电影:")
                for i, movie in enumerate(saved_movies[:10], 1):
                    logger.info(f"{i}. {movie['title']} - {movie['rating']}分")
            
            logger.info("数据保存成功！")
        else:
            logger.warning("未获取到任何电影数据")
    
    except Exception as e:
        logger.error(f"程序运行出错: {e}", exc_info=True)
        raise
    finally:
        logger.info("=" * 50)
        logger.info("豆瓣电影Top250爬虫结束")
        logger.info("=" * 50)

if __name__ == "__main__":
    main()
