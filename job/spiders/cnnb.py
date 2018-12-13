# -*- coding: utf-8 -*-
import re
from datetime import datetime

import scrapy

from job.items import JobItem


class CnnbSpider(scrapy.Spider):
    name = "cnnb"
    allowed_domains = ["bbs.cnnb.com"]
    start_urls = [
        'http://bbs.cnnb.com/forum.php?mod=forumdisplay&fid=37&filter=author&orderby=dateline&typeid=366&page=1',
        'http://bbs.cnnb.com/forum.php?mod=forumdisplay&fid=37&filter=author&orderby=dateline&typeid=103&page=1']

    def parse(self, response):
        '''
        解析目录
        @param response 下载的网页内容
        '''
        # 解析帖子链接
        links = response.xpath("//th/a[2]/@href").extract()

        # 解析每一个连接的帖子内容
        for each in links:
            yield scrapy.Request(each, callback=self.parse_content)
        # 下一页
        next_page = response.xpath('//a[@class="nxt"]/@href').extract_first()
        if next_page:
            yield scrapy.Request(next_page, callback=self.parse)

    def parse_content(self, response):
        '''
        解析帖子详情
        @param response 下载的网页内容
        yield jobitem 所需结果
        '''
        jobitem = JobItem()
        jobitem['link'] = response.url
        jobitem['title'] = self._get_title(response)
        jobitem['pub_date'] = self._get_date(response)
        jobitem['content'] = self._get_content(response)
        jobitem['phone'] = self._get_phone(jobitem['content'])
        jobitem['email'] = self._get_email(jobitem['content'])
        jobitem['crawl_date'] = datetime.today().strftime('%Y-%m-%d')
        yield jobitem

    def _get_title(self, response):
        '''
        获取标题
        @param response 下载的网页内容
        return str 返回标题
        '''
        title = response.xpath(
            '//*[@id="thread_subject"]/text()').extract_first()
        return title.strip()

    def _get_date(self, response):
        '''
        获取日期
        @param response 下载的网页内容
        return str 返回日期
        '''
        date = response.xpath(
            '//*[@class="authi"]/em/span/@title').extract_first()
        if not date:
            date = response.xpath(
                '//*[@class="authi"]/em/text()').extract_first()
        return date.replace('发表于 ', '')

    def _get_content(self, response):
        '''
        获取帖子详情
        @param response 下载的网页内容
        return str 返回详情
        '''
        content = response.xpath('//td[@class="t_f"]//text()').extract()
        return ' '.join((' '.join(i.split()) for i in content)).replace('\\r', '')

    def _get_phone(self, content):
        '''
        获取手机或座机号码
        @param response 解析的帖子详情
        return list 返回电话号码列表
        '''
        regex = r"[86]?1[34578]\d{9}|0\d{2,3}[\s\-]?\d{7,8}"
        return re.findall(regex, content)

    def _get_email(self, content):
        '''
        获取邮箱地址
        @param response 解析的帖子详情
        return list 返回邮箱地址列表
        '''
        regex = r"([a-zA-Z0-9_.+-]+@[a-pr-zA-PRZ0-9-]+\.[a-zA-Z0-9-.]+)"
        email = re.findall(regex, content)
        return email
