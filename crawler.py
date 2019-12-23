from datetime import datetime
from time import sleep
import requests
from lxml import etree


class Crawler(object):
	def __init__(self,base_url='https://www.csie.ntu.edu.tw/news/',rel_url='news.php?class=101'):
		self.base_url = base_url
		self.rel_url = rel_url
	def crawl(self, start_date, end_date,
              date_thres=datetime(2012, 1, 1)):

		if start_date < date_thres:
			start_date = date_thres
		contents = list()
		page_num = 0
		while True:
			rets, last_date = self.crawl_page(start_date, end_date, page=f'&no={page_num}')
			page_num += 10
			if rets:
				contents += rets
			if last_date < start_date:
				break
		return contents

	def crawl_page(self, start_date, end_date, page=''):
		res = requests.get(self.base_url + self.rel_url + page, headers={'Accept-Language':'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6'}).content.decode()
		sleep(0.1)
		parser = etree.HTML(res)
		xpath = '/html/body/div[1]/div/div[2]/div/div/div[2]/div/table/tbody'
		root = parser.xpath(xpath)[0]
		dates = root.xpath('//tr/td[1]/text()')
		titles = root.xpath('//tr/td[2]/a/text()')
		rel_urls = root.xpath('//tr/td[2]/a/@href')
		d = root.xpath('//tr[10]/td[1]/text()')
		last_date = datetime.strptime(d[0],'%Y-%m-%d')
		contents = list()
		for date, title, rel_url in zip(dates, titles, rel_urls):
			if datetime.strptime(date,'%Y-%m-%d') < start_date:
				break
			url = self.base_url + rel_url
			content = self.crawl_content(url)
			contents.append((date,title,content))

		return contents, last_date

	def crawl_content(self, url):
		res = requests.get(url,headers={'Accept-Language':'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6'}).content.decode()
		parser = etree.HTML(res)
		xpath = '/html/body/div[1]/div/div[2]/div/div/div[2]/div/div[2]/text()'
		content = parser.xpath(xpath)
		content[0].replace('\r',' ').replace('\n',' ')
		return ' '.join(content)
		raise NotImplementedError
