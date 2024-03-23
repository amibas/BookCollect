# 通过python爬虫爬取豆瓣图书数据

## 1. 项目简介

本项目是一个爬取豆瓣图书数据的爬虧项目，主要爬取豆瓣图书的书名、作者、评分、评价人数、出版社、出版日期、价格等信息，将爬取的数据保存到本地文件中。

## 2. 项目环境

- Pycharm
- Python 3.12
- requests
- BeautifulSoup
- pandas

## 3. 如何使用

1. 安装Python环境
2. 安装requests、BeautifulSoup、pandas库

```shell
pip install -r requirements.txt
```

3.运行代码

```shell
python main.py
``` 

## 4. 项目配置

- 可以在main.py文件中配置爬取的图书url、爬取的页数

## 5. 注意事项

- 豆瓣在无登陆的情况下，爬取数据会有一定的限制，可能会出现验证码，所以建议在有登陆的情况下爬取数据，登录后的cookie可以通过浏览器的开发者工具获取，
并在代码中设置cookie
- 本项目仅供学习交流使用，不得用于商业用途