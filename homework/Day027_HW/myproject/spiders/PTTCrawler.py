import scrapy
from bs4 import BeautifulSoup
from ..items import PTTArticleItem as Item
import re
import time

class PttSpider(scrapy.Spider):
    name = 'PTTCrawler'
    #allowed_domains = ['https://www.ptt.cc/bbs/Gossiping/M.1577687305.A.E7E.html']
    def __init__(self,board='HatePolitics'):
        self.cookies = {'over18': '1'}
        self.start_urls = 'https://www.ptt.cc/bbs/{}/index.html'.format(board)
        self.host = 'https://www.ptt.cc'
    def start_requests(self):
        yield scrapy.Request(url=self.start_urls, callback=self.parse , cookies=self.cookies)
        
    def parse(self, response):
        soup = BeautifulSoup(response.body,features = 'lxml')
        mainList = soup.find('div',{'class':'r-list-container action-bar-margin bbs-screen'})
        articles = mainList.find_all('div')
        for article in articles:
            #print(article['class'][0])
            if 'r-ent' == article['class'][0]:
                if '本文已被刪除' not in article.text:
                    articleUrl = self.host + article.find('div',{'class':'title'}).a['href']
                    #print(articleUrl)
                    yield scrapy.Request(url=articleUrl, callback=self.parse_article , cookies=self.cookies)
                    #time.sleep(1)
            elif 'r-list-sep' == article['class'][0]:
                break
        
        
    def parse_article(self, response):
        #print(response)
        soup = BeautifulSoup(response.body,features = 'lxml')
        #item = response.css('span[class="article-meta-value"]::text').extract()
        createItem = Item()
        
        #取得文章相關資料
        article_detail = soup.find_all('span',{'class':'article-meta-value'})
        #if len(article_detail) > 0:
        #print(article_detail[2].text)
        createItem['author'] = article_detail[0].text
        createItem['plate'] = article_detail[1].text
        createItem['title'] = article_detail[2].text
        createItem['creatTime'] = article_detail[3].text
        
        #讀取文章本體
        fileTxt = ''
        x = ['作者','看板','標題','時間']
        main_list = soup.find('div',{'id':'main-content'})
        for line in main_list.stripped_strings:
            passTxt = False
            for item in createItem:
                if line in x or createItem[item] in line:
                    passTxt = True
            if line[0] not in [u'※', u'◆'] and line[:2] not in [u'--'] and not passTxt:
                fileTxt = '{0}\n{1}'.format(fileTxt,line)
            elif line[0] in u'→':
                break
        print(fileTxt)
        createItem['article'] = fileTxt
        #return createItem
