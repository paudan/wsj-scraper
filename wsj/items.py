# -*- coding: utf-8 -*-

import scrapy

class CompanyEntryItem(scrapy.Item):
    sector = scrapy.Field()
    company = scrapy.Field()
    country = scrapy.Field()
    pass
