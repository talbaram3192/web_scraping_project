from bs4 import BeautifulSoup
import requests
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

PATH = 'C:\Program Files\chromedriver.exe'

def read_urls():
    urls = list()
    urls.append('https://www.atptour.com/en/scores/results-archive?year=2020')
    return urls

def read_htmls(urls):
    htmls = list()
    for url in urls:
        driver = webdriver.Chrome(PATH)
        driver.get(url)
        table = driver.find_element_by_id('scoresResultsArchive')
        tbody = table.find_element_by_tag_name('tbody')
        tr = tbody.find_elements_by_tag_name('tr')
        for i in tr:
            td = i.find_element_by_class_name('title-content')
            print(td.text)
            print()


        driver.close()




        # source = requests.get(url).text
        # soup = BeautifulSoup(source, 'lxml')
        # print(soup.prettify())
        # file = open('tourn.html', 'w')
        # file.write(source)



def main():
    urls = read_urls()
    htmls = read_htmls(urls)



if __name__ == '__main__':
    main()

