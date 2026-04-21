# 豆瓣电影Top250爬虫

一个完整的豆瓣电影Top250数据爬虫项目，支持数据存入MySQL数据库，带有完整的日志系统。
*注意：此文件完全由Claude code接deepseek V3 API来完成，全程无人工修改代码*

## 项目结构

```
爬取豆瓣电影top100/
├── config.py          # 配置文件
├── logger.py          # 日志模块
├── database.py        # 数据库操作模块
├── spider.py          # 爬虫核心模块
├── main.py            # 程序入口
├── requirements.txt   # 依赖包列表
├── logs/              # 日志文件目录
├── db/                # 数据库相关
└── data/              # 数据目录
```

## 功能特性

- 爬取豆瓣电影Top250完整数据
- 自动创建MySQL数据库和表
- 支持数据去重和更新
- 完整的日志记录系统
- 模块化设计，易于扩展

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置数据库

编辑 `config.py` 文件，修改MySQL数据库连接信息：

```python

MYSQL_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '你的密码'),# 修改为你的密码
    'database': os.getenv('DB_DATABASE', 'douban_movies'),
    'charset': os.getenv('DB_CHARSET', 'utf8mb4')
}
```

## 运行程序

```bash
python main.py
```

## 数据库表结构

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键，自增 |
| rank | INT | 电影排名 |
| title | VARCHAR(255) | 电影标题 |
| director | VARCHAR(500) | 导演 |
| actors | TEXT | 主演 |
| year | VARCHAR(50) | 年份 |
| region | VARCHAR(255) | 地区 |
| genre | VARCHAR(255) | 类型 |
| rating | DECIMAL(3,1) | 评分 |
| rating_count | INT | 评价人数 |
| quote | TEXT | 一句话评价 |
| detail_url | VARCHAR(500) | 详情页链接 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

## 注意事项

1. 确保MySQL服务已启动
2. 确保数据库用户有创建数据库和表的权限
3. 程序有请求间隔控制，避免对豆瓣服务器造成压力
