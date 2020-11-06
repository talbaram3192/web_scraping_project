import requests
import os
from selenium import webdriver, common
from selenium.webdriver.common.keys import Keys
import time
import csv
import datetime
import sys

START_YEAR = 1877
PATH = '/usr/bin/chromedriver'
COLUMNS = ['Year', 'Name', 'Location', 'Dates', 'Draw- singles', 'Draw- doubles', 'Surface', 'Prize money',
           'Winner- singles', 'Winner- doubles', 'Winner- team', 'URL_Tournament']


def read_urls():
    """ read all relevant URLS from the ATP website and return a list of them """
    url_base = 'https://www.atptour.com/en/scores/results-archive?year='
    urls = list()
    cur_year = int(time.strftime("%Y"))  # current year
    year = START_YEAR
    while year <= cur_year:  # get all url pages from 1877
        urls.append(url_base + str(year))
        year += 1
    return urls


def extract_url_result(webelement_atp):
    """
    Takes a selenium class object (selenium.webdriver.remote.webelement.WebElement) of an atp website and extract
    the url to a webpage with detail results of each tournament. Return NA if it does not find the tag.
    """
    try:
        return webelement_atp.find_element_by_class_name('button-border').get_attribute('href')
    except common.exceptions.NoSuchElementException:
        return 'NA'


def create_csv(name, columns):
    """
    create a csv name_<dateoftoday>.csv
    """
    today = datetime.date.today().strftime('%d%m%Y')
    filename = "tournaments_data_" + today + '.csv'
    with open(filename, 'w') as csv_data:
        writer = csv.writer(csv_data)
        writer.writerow(COLUMNS)
    return filename


def general_tournament_data(url, name='tournament', test=True):
    """
    Extract general information about tournament of a particular year from ATP
    """
    filename = create_csv(name, COLUMNS)  # create csv file
    driver = webdriver.Chrome(PATH)
    driver.get(url)
    year = url.split('=')[1]
    print(f"scraping results from year {year}..")
    table = driver.find_element_by_id('scoresResultsArchive')
    tbody = table.find_element_by_tag_name('tbody')
    tr = tbody.find_elements_by_tag_name('tr')
    for i in tr:  # each 'tr' tag holds the relevant information regarding each tournament in the URL

        csv_data = open(filename, 'a')  # open our csv file
        writer = csv.writer(csv_data)

        td_content = i.find_element_by_class_name('title-content')  # basic details- name, location and dates
        name = td_content.find_element_by_class_name('tourney-title').text  # tournament's name
        location = td_content.find_element_by_class_name('tourney-location').text  # tournament's location
        dates = td_content.find_element_by_class_name('tourney-dates').text  # tournament's dates

        td_draw = i.find_elements_by_class_name('tourney-details')[0]  # number of participants in the draw
        draw_singles = td_draw.find_elements_by_tag_name('span')[0].text  # singles- draw
        draw_doubles = td_draw.find_elements_by_tag_name('span')[1].text  # doubles- draw

        surface = i.find_elements_by_class_name('tourney-details')[1].text  # surface type

        prize_money = i.find_elements_by_class_name('tourney-details')[2].text  # prize money

        td_winners = i.find_elements_by_class_name('tourney-details')[3]  # winners
        winners = td_winners.find_elements_by_class_name('tourney-detail-winner')
        # Extract URL_TOURNAMENT [ADD GABRIEL]
        url_tournament = extract_url_result(i)
        if len(winners) == 0:
            winner_singles = None  # if there aren't any winners (tournament didn't happen yet or
            winners_doubles = None  # got canceled)- don't save any winners
            winners_team = None
        elif len(winners) == 1:  # one winner- either singles, doubles or team
            if winners[0].text[:3] == 'SGL':
                winner_singles = winners[0].text[5:]
                winners_doubles = None
                winners_team = None
            elif winners[0].text[:3] == 'DBL':
                winner_singles = None
                winners_doubles = winners[0].text[5:]
                winners_team = None
            else:
                winner_singles = None
                winners_doubles = None
                winners_team = winners[0].text[6:]
        else:  # len=3. two winners- singles and doubles (there are no tournaments that include
            for winner in winners:  # singles, doubles and team winners)
                if winner.text[:3] == 'SGL':
                    winner_singles = winner.text[5:]
                else:
                    winners_doubles = winner.text[5:]
            winners_team = None

        new_row = [year, name, location, dates, draw_singles, draw_doubles, surface, prize_money,
                   winner_singles, winners_doubles, winners_team, url_tournament]

        writer.writerow(new_row)
        if test:
            print('Exit')
            csv_data.close()
            sys.exit(1)
    # data = open('tournaments_data.csv', 'r')   # check csv file
    # print(data.readlines())
    # data.close()
    # close our driver after finishing scraping the website
    csv_data.close()