import requests
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import csv

PATH = 'C:\Program Files\chromedriver.exe'
COLUMNS = ['Year', 'Name', 'Location', 'Dates', 'Draw- singles', 'Draw- doubles', 'Surface', 'Prize money',
           'Winner- singles', 'Winner- doubles', 'Winner- team']
START_YEAR = 1877

def read_urls():
    """ read all relevant URLS from the ATP website and return a list of them """
    url_base = 'https://www.atptour.com/en/scores/results-archive?year='
    urls = list()
    cur_year = int(time.strftime("%Y"))
    year = START_YEAR
    while year <= cur_year:   # get all url pages from 1877
        urls.append(url_base+str(year))
        year += 1
    return urls

def extract_urls(urls):
    """ extract tournaments data from all URLS in a list given and save on a csv file """

    csv_data = open('tournaments_data.csv', 'w')  # create csv file
    writer = csv.writer(csv_data)
    writer.writerow(COLUMNS)
    csv_data.close()

    for url in urls:
        year = url.split('=')[1]
        print(f"scraping results from year {year}..")
        driver = webdriver.Chrome(PATH)
        driver.get(url)
        table = driver.find_element_by_id('scoresResultsArchive')
        tbody = table.find_element_by_tag_name('tbody')
        tr = tbody.find_elements_by_tag_name('tr')
        for i in tr:     # each 'tr' tag holds the relevant information regarding each tournament in the URL

            csv_data = open('tournaments_data.csv', 'a')  # open our csv file
            writer = csv.writer(csv_data)

            td_content = i.find_element_by_class_name('title-content') # basic details- name, location and dates
            name = td_content.find_element_by_class_name('tourney-title').text  # tournament's name
            location = td_content.find_element_by_class_name('tourney-location').text # tournament's location
            dates = td_content.find_element_by_class_name('tourney-dates').text # tournament's dates

            td_draw = i.find_elements_by_class_name('tourney-details')[0]  # number of participants in the draw
            draw_singles = td_draw.find_elements_by_tag_name('span')[0].text # singles- draw
            draw_doubles = td_draw.find_elements_by_tag_name('span')[1].text # doubles- draw

            surface = i.find_elements_by_class_name('tourney-details')[1].text # surface type

            prize_money = i.find_elements_by_class_name('tourney-details')[2].text # prize money

            td_winners = i.find_elements_by_class_name('tourney-details')[3] #winners
            winners = td_winners.find_elements_by_class_name('tourney-detail-winner')
            if len(winners) == 1:
                winners_team = winners[0].text   # if its a 'team tournament'- save only the team winner
                winner_singles = None
                winners_doubles = None

            elif len(winners) == 2:               # if its a 'regular tournament'- save only the singles and
                winner_singles = winners[0].text  # doubles winners
                winners_doubles = winners[1].text
                winners_team = None

            else:                                # if there aren't any winners (tournament didnt happen yet or
                winner_singles = None            # got canceled)- don't save any winners
                winners_doubles = None
                winners_team = None


            new_row = [year, name, location, dates, draw_singles, draw_doubles, surface, prize_money,
                       winner_singles, winners_doubles, winners_team]

            writer.writerow(new_row)


        csv_data.close()
        # data = open('tournaments_data.csv', 'r')   # check csv file
        # print(data.readlines())
        # data.close()
        driver.close()   # close our driver after finishing scraping the website


def main():
    urls = read_urls()
    extract_urls(urls)


if __name__ == '__main__':
    main()

