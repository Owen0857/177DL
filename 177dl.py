#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-
__author__ = 'wudaown'

#
#   应朋友要求做了一个脚本从 www.177pic.info/ 下载所有中文漫画
#   已经挂服务器上面慢慢跑了，没有上面用处，一次性的东西
#

import requests
from bs4 import BeautifulSoup
from io import BytesIO
import os
from tqdm import tqdm, trange


def getSource(url):     # 读取完整页面 返回一个漫画名称和下载地址的mapping
    r = requests.get(url)
    soup = BeautifulSoup(r.text,'lxml')
    link = soup.find_all('h2', class_="grid-title")  # bs4 找 h2 tag
    dl = []
    title = []
    for x in link:
        title.append(x.string) # h2 tag 下还有其他tag读取内容
        dl.append(x.contents[0].attrs['href'])
    comic = dict(zip(dl,title))
    return(comic)

def getPageNumber(page_url):    # 通过下载地址判断一共有多少页
    allPage = []
    p = requests.get(page_url)
    pagesoup = BeautifulSoup(p.text,'lxml')
    page = pagesoup.find_all('div', class_='page-links')
    if page == None:    # 如果page值为空则返回默认页面
        number_of_page = 0
        allPage.append(page_url)
        return allPage
    else:
        number_of_page = 0;
        for p in page:
            for idx in range(1, len(p.contents)):   # TODO have to verify first and end page.
                if p.contents[idx].name == 'a':
                    allPage.append(p.contents[idx].attrs['href'])
        return allPage


def getImglink(page):       # 去的图片直链
    imgdr = []
    p = requests.get(page)
    imgsoup = BeautifulSoup(p.text,'lxml')
    imglink = imgsoup.findAll('img')    # 找html中所有图片
    for y in imglink:
        if 'data-lazy-src' in y.attrs:        # 剔除没有编号的图片
            imgdr.append(y['data-lazy-src'])
    return  imgdr


def downloadComic(comic_link, title):      # 下载图片
    imglist = []
    comic_page = getPageNumber(comic_link)
    for x in comic_page:
        tmp = getImglink(x)
        for y in tmp:
            imglist.append(y)

    imgbar = trange(len(imglist))
    imgbar.set_description(desc=title)
    for z in imgbar:      # 用range是因为要重命名图片为后面打包做准备
        #print(imglist[z], "   ", z)
        img = requests.get(imglist[z-1])
        if img.status_code == 200:
            with open(format(z,'03')+'.jpg', 'wb') as f: # 图片wb模式写入 binary
                f.write(img.content)
    os.chdir('..')

def main(): # main 模块
    url = 'http://www.177pic.info/html/category/tt/page/'
    end_page = 2
    url_list = []

    for i in range(end_page, 1, -1):    # 根据记录选择开始页面
        url_list.append(url+str(i))
    url_list.append('http://www.177pic.info/html/category/tt')      # main page.

    for y in url_list:
        #print('正在下载: ',y)
        comic = getSource(y)

        for x in comic:
            #print('正在下载: ', comic[x])
            if (os.path.exists(comic[x])) == True:
                #print('目录已经存在。')
                os.chdir(comic[x])
                downloadComic(x, comic[x])
                #command = 'rar a -r -s -m5 -df \''+comic[x]+'.cbr\' \''+comic[x]+'\''
                #os.system(command)
                #os.system('clear')
            else:
                os.mkdir(comic[x])
                os.chdir(comic[x])
                downloadComic(x, comic[x])
                #command = 'rar a -r -s -m5 -df \''+comic[x]+'.cbr\' \''+comic[x]+'\''
                #os.system(command)
                #os.system('clear')

if __name__ == '__main__':
    main()

