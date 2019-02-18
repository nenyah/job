# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JobItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    link = scrapy.Field() #帖子连接
    author = scrapy.Field() #发贴人
    title = scrapy.Field() #标题
    pub_date = scrapy.Field() #发布日期
    content = scrapy.Field() #内容
    phone = scrapy.Field() # 电话
    email = scrapy.Field() # 邮箱
    crawl_date = scrapy.Field() #采集日期
