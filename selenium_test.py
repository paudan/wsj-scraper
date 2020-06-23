from shutil import which
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup

url = 'https://www.wsj.com/market-data/quotes/company-list/'

options = FirefoxOptions()
options.headless = True
driver = webdriver.Firefox(executable_path=which('geckodriver'), options=options)
driver.get(url)
WebDriverWait(driver, 5).until(lambda s: driver.find_element_by_class_name('index-sector').is_displayed())
bs = BeautifulSoup(driver.page_source, "lxml")
index = bs.select('.index-sector')
if index and len(index) > 0:
    index = index[0]
urls = [a['href'] for a in index.find_all('a')]
print(urls)
# sector = bs.select('.border-box > h3')
# if sector:
#     sector = sector[0].get_text()
# print(sector)
# table = bs.select('.cl-table')
# table = table[0]
# rows = table.find("tbody").find_all("tr")
# for row in rows:
#     td = row.find_all('td')
#     if len(td) < 2:
#         continue
#     company = td[0].get_text()
#     country = td[1].get_text()
#     print(company, country)
driver.close()