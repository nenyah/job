# -*- coding: utf-8 -*-
import re
from datetime import datetime

import scrapy

from job.items import JobItem


class CnnbSpider(scrapy.Spider):
    name = "cnnb"
    allowed_domains = ["bbs.cnnb.com"]
    start_urls = [
        'https://bbs.cnnb.com/forum.php?mod=forumdisplay&fid=37&typeid=103&filter=typeid&typeid=103&page=1',
        'https://bbs.cnnb.com/forum.php?mod=forumdisplay&fid=37&typeid=366&filter=typeid&typeid=366&page=1'
    ]

    def parse(self, response):
        '''
        解析目录
        @param response 下载的网页内容
        '''
        # 解析帖子链接
        links = response.xpath("//*[contains(@id,'normalthread')]//th/a[2]/@href").extract()

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
        jobitem['author'] = self._get_author(response)
        jobitem['title'] = self._get_title(response)
        jobitem['pub_date'] = self._get_date(response)
        jobitem['content'] = self._get_content(response)
        jobitem['phone'] = self._get_phone(jobitem['content'])
        jobitem['email'] = self._get_email(jobitem['content'])
        jobitem['crawl_date'] = datetime.today().strftime('%Y-%m-%d')
        yield jobitem

    def _get_author(self, response):
        '''
        获取发贴人
        @param response 下载的网页内容
        return str 返回发贴人
        '''
        rule = '//*[@class="authi"]/a/text()'
        return response.xpath(rule).extract_first()
        # return self._extract_info(rule, response)

    def _get_title(self, response):
        '''
        获取标题
        @param response 下载的网页内容
        return str 返回标题
        '''
        rule = '//*[@id="thread_subject"]/text()'
        return self._extract_info(rule, response)

    def _get_date(self, response):
        '''
        获取日期
        @param response 下载的网页内容
        return str 返回日期
        '''
        rule1 = '//*[@class="plhin first"]//em/span/@title'
        rule2 = '//*[@class="authi"]/em/text()'
        date = self._extract_info(rule1, response)
        if not date:
            date = self._extract_info(rule2, response)
        if date:
            return date.replace('发表于 ', '')
        else:
            return None
    def _get_content(self, response):
        '''
        获取帖子详情
        @param response 下载的网页内容
        return str 返回详情
        '''
        rule = '//*[@class="plhin first"]//td[@class="t_f"]//text()'
        content = response.xpath(rule).extract()
        return ''.join(content)

    def _get_phone(self, content):
        '''
        获取手机或座机号码
        @param response 解析的帖子详情
        return list 返回电话号码列表
        '''
        regex = r'(?:13[\d]|14[579]|15[0-3,5-9]|16[6]|17[0135678]|18[0-9]|19[89])\d{8}|(?<=电话)(?:\d{4}[\-|\s])?\d{8}|(?<=电话：)(?:\d{4}[\-|\s])?\d{8}'
        return re.findall(regex, content)

    def _get_email(self, content):
        '''
        获取邮箱地址
        @param response 解析的帖子详情
        return list 返回邮箱地址列表
        '''
        regex = r"\w+\@\w+[\.\w+]+"
        email = re.findall(regex, content)
        return email

    def _extract_info(self, rule, response):
        '''
        按抽取规则抽取内容
        @param rule 规则
        return str 返回内容
        '''
        content = response.xpath(rule).extract_first()
        if content:
            content = content.strip()
        return content
