# -*- coding: utf-8 -*-
from shutil import which
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from wsj.items import CompanyEntryItem


STARTING_URL = 'https://www.wsj.com/market-data/quotes/company-list/'

def get_driver():
    options = FirefoxOptions()
    options.headless = True
    return webdriver.Firefox(executable_path=which('geckodriver'), options=options)

def process_page(response, driver):
    driver.get(response.url)
    WebDriverWait(driver, 20).until(lambda s: driver.find_element_by_class_name('cl-table').is_displayed())
    bs = BeautifulSoup(driver.page_source, "lxml")
    sector = bs.select('.border-box > h3')
    if sector:
        sector = sector[0].get_text()
    else:
        sector = None
    print(sector)
    table = bs.select('.cl-table')
    table = table[0]
    rows = table.find("tbody").find_all("tr")
    for row in rows:
        td = row.find_all('td')
        if len(td) < 2:
            continue
        yield CompanyEntryItem(sector = sector, company = td[0].get_text(), country = td[1].get_text())


class CompanyListSpider(CrawlSpider):
    name = 'company-list'
    allowed_domains = ['wsj.com']

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.driver = get_driver()
        # Pages which do not have pagination
        single_page = ['fishing', 'luxury-goods', 'general-services', 'watches-clocks-parts', 'alternative-fuel', 'tourism', 'water-utilities']
        self.start_urls = [STARTING_URL + 'sector/' + url for url in single_page]

    def __del__(self):
        if self.driver:
            self.driver.close()

    def parse(self, response):
        return process_page(response, self.driver)


class PaginatedCompanyListSpider(CrawlSpider):
    name = 'paginated-company-list'
    allowed_domains = ['wsj.com']
    rules = (
        Rule(LinkExtractor(allow=(), restrict_xpaths=('//li[@class="active"]/a',)), callback='parse_item', follow=True),
        Rule(LinkExtractor(allow=(), restrict_xpaths=('//li[@class="next"]/a',)), callback='parse_item', follow=True)
    )

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.driver = get_driver()
        self.start_urls = self.get_urls()

    def get_urls(self):
        self.driver.get(STARTING_URL)
        WebDriverWait(self.driver, 15).until(lambda s: self.driver.find_element_by_class_name('index-sector').is_displayed())
        bs = BeautifulSoup(self.driver.page_source, "lxml")
        index = bs.select('.index-sector')
        if not index or len(index) == 0:
            return list()
        return [a['href'] for a in index[0].find_all('a')]

    def parse_item(self, response):
        return process_page(response, self.driver)