from pyquery import PyQuery as Pq
import requests
import os
import threading
import time
import re


class DownOnePage(threading.Thread):
    def __init__(self, thread_id, name, title, url):
        threading.Thread.__init__(self)
        self.threadID = thread_id
        self.name = name
        self.title = title
        self.url = url

    def run(self, *args):
        img_num = 1
        url_p = self.url + "/" + str(self.threadID) + "/"
        e = query_html(url_p)
        if e[0] == 1:
            e = Pq(e[1])
            img_list = e('.single-content')('img').items()
            for j in img_list:
                img_url = (j.attr("src"))
                r = requests.get(img_url)
                img_name = "{}_{}.jpg".format(str(self.threadID), str(img_num))
                path = os.path.join(self.title, img_name)
                with open(path, 'wb') as f:
                    f.write(r.content)
                img_num += 1
                counter.plus()
                print_progress(counter.count, counter.total, suffix='Complete', bar_length=50)
        else:
            pass


class Counter(object):
    def __init__(self):
        self.total = 0
        self.count = 0

    def reset(self, total):
        self.total = total
        self.count = 0

    def plus(self):
        self.count += 1


counter = Counter()


def query_html(url):
    """
    请求网页
    :param url: str
    :return: list [int, bytes]
    """
    headers = {
        'user-agent': '''
        Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 
        (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36 
        Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8''',
    }
    try:
        r = requests.get(url, headers)
        return [1, r.content]
    except Exception as e:
        print("连接失败。请确定你可以访问网站(http://www.177pic.info)，或尝试将梯子设置为全局模式。")
        return [0, ""]


# 一个打印进度条的方法
def print_progress(iteration, total, prefix='', suffix='', decimals=1, bar_length=100):
    """
    Call in a loop to create a terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        barLength   - Optional  : character length of bar (Int)
    """
    import sys
    format_str = "{0:." + str(decimals) + "f}"
    percent = format_str.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '#' * filled_length + '-' * (bar_length - filled_length)
    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percent, '%', suffix)),
    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()


# 使用多线程来加快下载速度，每页开一个线程
def init_threads(page_num, title, url):
    threads = []
    for i in range(1, page_num):
        thread = DownOnePage(i, 'page_' + str(i), title, url)
        threads.append(thread)
    for i in threads:
        i.start()
    for i in threads:
        i.join()


def dl(mid):
    """
    下载
    :param mid: str 资源的编号
    :return:
    """
    url = "http://www.177pic.info/html/" + str(mid) + ".html"
    s = time.time()     # 计算耗时的时间戳
    e = query_html(url)
    if e[0] == 1:
        e = Pq(e[1])
        title = e('.entry-title').eq(0)
        if title:
            title = title.text()
        else:
            return "资源不存在，请检查是否输入有误"

        print("标题：{}".format(title))
        match_obj = re.search(r'\[(\d+)P\]', title)
        a = "未知"
        if match_obj is not None:
            a = match_obj.group(1)
        print("共 {} 张图片".format(a))
        if a != "未知":
            counter.reset(int(a))
        # print("获取总页数……")
        page_link_list = e('.page-links').find('a')
        page_num = page_link_list.length
        # print("总页数 ", page_num - 1)

        print("开始下载……")
        if not os.path.exists(title):
            os.makedirs(title)
        init_threads(page_num, title, url)
        d = time.time()
        return "耗时{}S".format(round(d - s, 4))
    else:
        pass


def get_index(page, manga=False):
    """
    获取索引
    :param page: list/int 指定页数(范围)
    :param manga: bool 是否只返回漫画资源
    :return:
    """
    try:
        if type(page) is list:
            start = int(page[0])
            end = int(page[1])
        else:
            start = int(page)
            end = start
    except ValueError as e:
        print("页码只能是数字")
        return

    for j in range(start, end + 1):
        print("page {}".format(j))
        url = "http://www.177pic.info/html/category/tt/page/{}/".format(j)
        e = query_html(url)
        if e[0] == 1:
            e = Pq(e[1])
            items = e('.picture-img').items()
            for i in items:
                img_src, title = i('img').attr('src'), i('img').attr('alt')
                if manga is True:
                    if title[0] != "[":
                        continue
                m_info = i('a').eq(2)
                m_id = m_info.attr('href').split("html/")[1].split('.')[0]
                print(m_id, title, "\t")
        else:
            pass


def user_help():
    """
    说明
    :return:
    """
    print("""
index [n=1]
    获取某页列表
    n 取值整数，不填默认为 1

    示例：
    index
    index 2

manga_index [n=1, m=n]
    获取某页列表，只返回漫画资源，并不完全正确。
    n 为整数，不填默认获取第一页
    m 为整数，默认等于n，以为从第 n 页到第 m 页

    示例：
    manga_index
    manga_index 2
    manga_index 3 5

dl 资源id
    资源id为index 命令返回的 "yyyy/mm/xxxxxxx" 格式的字符串
    
    示例：dl 2020/05/1234567

建议使用方法：浏览器访问网站找到要下载的资源id(浏览器地址栏复制)，直接使用 dl 命令下载
 """)


def split_arg(arg):
    return arg.split(" ")


def main():
    print("输入 help 获取帮助")
    while True:
        arg = input("等待输入：")
        args = split_arg(arg)
        if args[0] == "index":
            try:
                page = args[1]
            except IndexError:
                page = "1"
            get_index(page)
        elif args[0] == "manga_index":
            try:
                page_s = args[1]
            except IndexError:
                page_s = "1"
            try:
                page_e = args[2]
            except IndexError:
                page_e = page_s
            get_index([page_s, page_e], manga=True)
        elif args[0] == "dl":
            m_id = args[1]
            print(dl(m_id))
        elif args[0] == "exit":
            print("bye")
            time.sleep(1)
            break
        elif args[0] == "help":
            user_help()
        else:
            print("命令不存在，输入 help 获取帮助")


if __name__ == "__main__":
    main()
