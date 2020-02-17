import os
from hashlib import md5
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
import re
from mongo_config import *
import pymongo

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

def save_to_mongo(result):
    if db[MONGO_TABLE].insert(result):
        print('存储成功',result)
        return True
    return False

def get_one_page(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36'}
        response = requests.get(url,headers=headers)
        response.encoding = 'gb2312'
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            return soup
        return None
    except RequestException:
        return None

def get_one_theme(url):
    # 创建数据字典
    dic = dict()
    dic.update({'url':url})
    soup = get_one_page(url)
    soup1 = soup.find('div', attrs={'class': 'picsbox picsboxcenter'})
    # alt = "性感姐妹花Angela楚楚&amp;金露J半透美乳清纱互相调情养眼"
    # src = "https://img.lovebuy99.com/uploads/allimg/200130/15-200130023103.jpg"
    title = re.search('alt="(.*?)"', str(soup1), re.S)
    print(title.group(0).split("\"")[1])
    src = re.search('src="(.*?)"/>', str(soup1), re.S)
    print(src.group(0).split("\"")[1])
    list1 = []
    list1.append(src.group(0).split("\"")[1])
    dic.update({'title':title.group(0).split("\"")[1]})

    # 处理页数循环爬取
    soup2 = soup.find('div', attrs={'class': 'itempage'})
    page_no = re.search('.*?([0-9]+)', str(soup2), re.S)
    num = int(page_no.group(0).split('共')[1])

    for i in range(2, num):
        res = url + 'index_' + str(i) + '.html'
        soup = get_one_page(res)
        soup1 = soup.find('div', attrs={'class': 'picsbox picsboxcenter'})
        # alt = "性感姐妹花Angela楚楚&amp;金露J半透美乳清纱互相调情养眼"
        # src = "https://img.lovebuy99.com/uploads/allimg/200130/15-200130023103.jpg"
        title = re.search('alt="(.*?)"', str(soup1), re.S)
        #print(title.group(0).split("\"")[1])
        src = re.search('src="(.*?)"/>', str(soup1), re.S)
        #print(src.group(0).split("\"")[1])
        download_images(src.group(0).split("\"")[1],title.group(0).split("\"")[1])
        list1.append(src.group(0).split("\"")[1])
    dic.update({'image': list1})
    #print(dic)
    save_to_mongo(dic)

def download_images(url,name):
    print('正在下载',url)
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36'}
        response = requests.get(url,headers=headers)
        response.encoding = 'gb2312'
        if response.status_code == 200:
            save_images(response.content,name)
        return None
    except RequestException:
        return None

def save_images(content,name):
    isExists = os.path.exists(os.getcwd()+"\\"+str(name))
    if not isExists:
        os.makedirs(os.getcwd()+"\\"+str(name))
    file_path = '{0}/{1}.{2}'.format(os.getcwd()+"\\"+str(name),md5(content).hexdigest(),'jpg')
    if not os.path.exists(file_path):
        with open(file_path,'wb') as f:
            f.write(content)
            f.close()

def main():
    for i in range(1,2):
        url = 'https://www.7160.com/zhenrenxiu/list_11_'+ str(i) +'.html'
        soup = get_one_page(url)
        soup1 = soup.find('div',attrs={'class': 'news_bom-left'})
        src = re.findall('/zhenrenxiu/[0-9]+/', str(soup1), re.S)
        for list in src:
            theme_url = 'https://www.7160.com' + list
            get_one_theme(theme_url)




if __name__ == '__main__':
    main()