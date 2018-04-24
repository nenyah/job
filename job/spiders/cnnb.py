# -*- coding: utf-8 -*-
import scrapy
from job.items import JobItem
import re


class CnnbSpider(scrapy.Spider):
    name = "cnnb"
    allowed_domains = ["bbs.cnnb.com"]
    start_urls = [
        'http://bbs.cnnb.com/forum.php?mod=forumdisplay&fid=37&filter=author&orderby=dateline&typeid=366&page=1',
        'http://bbs.cnnb.com/forum.php?mod=forumdisplay&fid=37&filter=author&orderby=dateline&typeid=103&page=1']

    def parse(self, response):
        # 解析帖子链接
        links = response.xpath("//th/a[2]/@href").extract()

        # 解析每一个连接的帖子内容
        for each in links:
            yield scrapy.Request(each, callback=self.parse_content)
        #下一页
        next_page = response.xpath('//a[@class="nxt"]/@href').extract_first()
        if next_page:
            yield scrapy.Request(next_page, callback=self.parse)

    def parse_content(self, response):
        jobitem = JobItem()
        jobitem['link'] = response.url
        # 这里依然可以用extract(),不过exract()返回的是列表，extract_first()返回的是字符串
        jobitem['title'] = response.xpath(
            '//*[@id="thread_subject"]/text()').extract_first()
        jobitem['date'] = response.xpath(
            '//*[@class="authi"]/em/span/@title').extract_first()
        jobitem['content'] = self._get_content(response)
        # jobitem['phone'] = self._get_phone(jobitem['content'])
        # jobitem['email'] = self._get_email(jobitem['content'])
        yield jobitem

    def _get_content(self, response):
        content = response.xpath('//td[@class="t_f"]//text()').extract()
        return ''.join(content).replace('\r', '').replace('\n', '')

    def _get_phone(self, content):
        return re.findall(r"([0?[13|14|15|18][0-9]{9}]|[[0-9-()（）]{7,18}])", content)

    def _get_email(self, content):
        return re.findall(r"(\w[-\w.+]*@([A-Za-z0-9][-A-Za-z0-9]+\.)+[A-Za-z]{2,14})", content)
