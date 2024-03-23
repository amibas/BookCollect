import re

import requests
from bs4 import BeautifulSoup
from pandas import DataFrame
from tqdm import tqdm

# 小说类别的url
__url_novels__ = "https://book.douban.com/tag/%E5%B0%8F%E8%AF%B4?start=0&type=T"
# 历史类别的url
__url_history__ = "https://book.douban.com/tag/%E5%8E%86%E5%8F%B2?start=0&type=T"
# 哲学类别的url
__url_philosophy__ = "https://book.douban.com/tag/%E5%93%B2%E5%AD%A6?start=0&type=T"


class DoubanCrawler:
    send_headers = {
        "Host": "book.douban.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Connection": "close",
        "Cookie": """viewed="36153222"; bid=JXDK2yM7PkQ; ll="118318"; dbcl2="269401606:BmjIPaAKKv4"; push_noty_num=0; push_doumail_num=0; ck=JVDD; ct=y"""

    }

    def __init__(self, url, pages):
        """
        :param url: 爬虫的最初界面，决定了要爬的书籍的类别信息
        :param pages: 要爬取的页数，豆瓣每页20本书的信息，决定了要爬取的数据量
        """

        self.url = url
        self.pages = [20 * i for i in range(pages)]
        self.book_class = ""
        self.book_names = []
        self.book_nations = []
        self.book_writers = []
        self.book_scores = []
        self.book_comments = []
        self.book_sites = []
        self.book_pages = []

    def generate_urls(self):
        """
        生成要爬取的所有url列表
        """

        idx_urls = []
        # 正则表达式
        page_key = re.compile(r"(\S*\?)")
        # 利用正则表达式匹配出url的必须部分，后面和控制页数的变量进行拼接成索要检索的所有url列表
        # 注意利用正则匹配到的返回结果为一个列表，一般需要取出列表中的值进行下面的操作
        page_main = page_key.findall(self.url)[0]
        # “合成”所有url列表,因为豆瓣的规则是每20本书放在一页中，并且用url中的start关键字控制显示的页数
        for i in self.pages:
            g_url = page_main + "start=" + str(i) + "&type=T"
            idx_urls.append(g_url)
        return idx_urls

    def get_main_info(self, url):
        """
        获取url列表页面能获取主要信息，不打开各本书的独立页面，
        主要信息包括：书的所属类别，作者国家，书名，每本书的索引url，书的作者，书的评分，书的简介，书的页数
        :return: 各个主要信息的存储列表
        """

        # 分别为，书类别，国家，作者和简介的正则表示式
        global book_class, book_nation
        book_class_key = re.compile(": (\D*)")
        book_nation_key = re.compile("\[(\D*?)")
        book_writer_key1 = re.compile("^(\D*?)/")
        book_writer_key2 = re.compile("](\D*)$")
        book_comment_key = re.compile(r"<p>(\S*)</p>")
        # 创建存储主要信息的列表：因为书名是固定的，一个大页面是一个类别，所以只需要返回一次，不需要列表存储
        book_names = []
        book_pages = []
        book_nations = []
        book_writers = []
        book_comments = []
        book_scores = []

        resp = requests.get(url, headers=self.send_headers)  # 和上面一样的操作，向url发送get请求

        resp_text = resp.text  # 获取返回的文本信息

        soup = BeautifulSoup(resp_text, "lxml")  # 利用BS库对html格式的文本信息进行解析

        # 获取图书类别
        book_class = soup.find("h1").get_text()
        book_class = book_class_key.findall(book_class)

        # 获取图书列表
        book_list = soup.find_all("li", attrs={"class": "subject-item"})

        for book in book_list:
            book_info = book.find("div", attrs={"class": "info"})
            # 获取书名
            book_name = book_info.find("a").get("title")
            book_names.append(book_name)
            # 获取书的url
            book_url = book_info.find("a").get("href")
            book_pages.append(book_url)
            # 获取书的作者和国籍
            book_writer = book_info.find("div", attrs={"class": "pub"}).get_text()
            book_writer = book_writer.split("/")[0].strip()
            if '[' in book_writer:
                book_nation = book_writer.split(" ")[0]
                book_nation = book_nation[1].strip()
                book_writer = book_writer.split(']')[1].strip()
            else:
                book_nation = "中"
            book_writers.append(book_writer)
            book_nations.append(book_nation)

            # 获取书籍简介
            if not book.find("p"):
                book_comments.append("无简介")
            else:
                book_comments.append(book.find("p").get_text())
            # 获取书籍评分
            book_scores.append(book.find("span", attrs={"class": "rating_nums"}).get_text())

        return book_names, book_pages, book_class * 20, book_writers, book_nations, book_comments, book_scores

    def get_page_numbers(self, urls):
        """
        从每个图书的独立页面中获取数据，目前只获取了页数数据
        :param urls: 从get_main_info中生成的图书独立页面url列表
        :return: 对应图书的页数数据
        """
        book_pages_number = []
        print("****开始获取页数信息****")
        for url in tqdm(urls):
            request = requests.get(url, headers=self.send_headers)
            text = request.text
            in_soup = BeautifulSoup(text, 'lxml')
            # print(in_soup.text)
            page_num = re.compile(r"页数: (\d*)").findall(in_soup.text)
            # 有可能有的书缺失页数信息，遇上此类情况全部将页数设置为0
            if not page_num:
                book_pages_number.append(0)
            else:
                book_pages_number.extend(page_num)

        return book_pages_number

    def begin_crawl(self):
        """
        类的“主函数”只需要执行这个函数就可以完成爬虫功能
        :return: 所有的信息列表
        """
        sum_book_names = []
        sum_book_urls = []
        sum_book_class = []
        sum_book_writers = []
        sum_book_nations = []
        sum_book_comments = []
        sum_book_scores = []
        sum_book_pages = []
        urls = self.generate_urls()  # 生成要爬取的所有页面的url地址
        print("****开始爬取****")
        for url in tqdm(urls):
            (book_names,
             book_urls,
             book_class,
             book_writers,
             book_nations,
             book_comments,
             book_scores) = self.get_main_info(url)
            book_pages = self.get_page_numbers(book_urls)

            sum_book_names.extend(book_names)
            sum_book_urls.extend(book_urls)
            sum_book_class.extend(book_class)
            sum_book_writers.extend(book_writers)
            sum_book_nations.extend(book_nations)
            sum_book_comments.extend(book_comments)
            sum_book_scores.extend(book_scores)
            sum_book_pages.extend(book_pages)

        return (sum_book_names,
                sum_book_urls,
                sum_book_class,
                sum_book_writers,
                sum_book_nations,
                sum_book_comments,
                sum_book_scores,
                sum_book_pages)

    def write2csv(self):
        """
        将爬取结果写入csv文件中
        :return: 无返回值
        """
        name, url, book_class, writer, nation, comment, score, pages = self.begin_crawl()
        info_df = DataFrame(columns=["name", "url", "class", "writer", "nation", "comment", "score", "pages"])
        info_df["name"] = name
        info_df["url"] = url
        info_df["class"] = book_class
        info_df["writer"] = writer
        info_df["nation"] = nation
        info_df["comment"] = comment
        info_df["score"] = score
        info_df["pages"] = pages

        info_df.to_csv(f"{book_class[0]}.csv", header=None, encoding="utf_8_sig")


if __name__ == '__main__':
    # url：爬取的页面
    # pages：爬取的页数
    db_crawler = DoubanCrawler(__url_history__, 2)
    db_crawler.write2csv()
