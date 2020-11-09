import requests
import os
from selenium import webdriver, common
from selenium.webdriver.common.keys import Keys
import time
import csv
import datetime
import sys


PATH = 'C:\Program Files\chromedriver.exe'
COLUMNS = ['Year', 'Name', 'Location', 'Dates', 'Draw- singles', 'Draw- doubles', 'Surface', 'Prize money',
           'Winner- singles', 'Winner- doubles', 'Winner- team']
START_YEAR = 2020
PLAYERS = list()   # list that will contain the winners profile links


def read_urls():
    """ read all relevant URLS from the ATP website and return a list of them """
    url_base = 'https://www.atptour.com/en/scores/results-archive?year='
    urls = list()
    cur_year = int(time.strftime("%Y"))  # current year
    year = START_YEAR
    while year <= cur_year:            # get all url pages from 1877
        urls.append(url_base+str(year))
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


def create_csv(name):
    """
    create a csv name_<dateoftoday>.csv
    """
    today = datetime.date.today().strftime('%d%m%Y')
    filename = name + " tournaments_data_" + today + '.csv'
    with open(filename, 'w') as csv_data:
        writer = csv.writer(csv_data)
        writer.writerow(COLUMNS)
    return filename


def get_players_info():
    """ Get players information from their profiles """
    for url in PLAYERS:
        driver = webdriver.Chrome(PATH)
        driver.get(url)
        try:
            first = driver.find_element_by_class_name('first-name').text
            print(first)
        except:
            first = 'NA'
            pass
        try:
            last = driver.find_element_by_class_name('last-name').text
            print(last)
        except:
            last = 'NA'
            pass
        try:
            ranking_type = driver.find_element_by_class_name('hero-rank-label').text  # ranking type
            print(ranking_type)
        except:
            ranking_type = 'NA'
            pass
        try:
            ranking = driver.find_element_by_class_name('data-number').text # ranking
            print(ranking)
        except:
            ranking = 'NA'
            pass
        try:
            country = driver.find_element_by_class_name('player-flag-code').text # country
            print(country)
        except:
            country = 'NA'
            pass
        try:
            date_birth = driver.find_element_by_class_name('table-birthday').text.strip('()')  # date of birth
            print(date_birth)
        except:
            date_birth = 'NA'
            pass
        try:
            turned_pro = driver.find_elements_by_class_name('table-big-value')[1].text # turned pro
            print(turned_pro)
        except:
            turned_pro = 'NA'
            pass
        try:
            weight = driver.find_element_by_class_name('table-weight-lbs').text  # weight
            print(weight)
        except:
            weight = 'NA'
            pass
        try:
            height = driver.find_element_by_class_name('table-height-ft').text  # height
            print(height)
        except:
            height = 'NA'
            pass
        try:
            total_prize_money = driver.find_elements_by_class_name('stat-value')[8].text.split()[0] # total prize money
            print(total_prize_money)
        except:
            total_prize_money = 'NA'
            pass

        print()
        print()
        driver.close()


def general_tournament_data(url, filename):
    """
    Extract general information about tournament of a particular year from ATP
    """
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
                try:  # get players links to profiles
                    winner_profile = winners[0].find_element_by_tag_name('a').get_attribute('href')
                    if winner_profile not in PLAYERS:
                        PLAYERS.append(winner_profile)
                except:
                    pass   # link doesn't exist

            elif winners[0].text[:3] == 'DBL':
                winner_singles = None
                winners_doubles = winners[0].text[5:]
                winners_team = None

                try:     # get players links to profiles
                    a_tags = winners[0].find_element_by_tag_name('a')
                    for a in a_tags:
                        if a.get_attribute('href') not in PLAYERS:
                            PLAYERS.append(a.get_attribute('href'))
                except:
                    pass  # links don't exist
            else:
                winner_singles = None
                winners_doubles = None
                winners_team = winners[0].text[6:]   # teams dont have profiles so there's no links to add
                                                     # in this case

        else:  # len=3. two types of winners- singles and doubles (there are no tournaments that include
            for winner in winners:  # singles, doubles and team winners)
                if winner.text[:3] == 'SGL':
                    winner_singles = winner.text[5:]
                    try:   # get players links to profiles
                        winner_profile = winner.find_element_by_tag_name('a').get_attribute('href')
                        if winner_profile not in PLAYERS:
                            PLAYERS.append(winner_profile)
                    except:
                        pass   # link doesn't exist
                else:
                    winners_doubles = winner.text[5:]
                    try:   # get players links to profiles
                        a_tags = winner.find_elements_by_tag_name('a')
                        for a in a_tags:
                            if a.get_attribute('href') not in PLAYERS:
                                PLAYERS.append(a.get_attribute('href'))
                    except:
                        pass  # links don't exist

            winners_team = None

        new_row = [year, name, location, dates, draw_singles, draw_doubles, surface, prize_money,
                   winner_singles, winners_doubles, winners_team, url_tournament]

        writer.writerow(new_row)

    csv_data.close()
    driver.close()


def main():
    urls = read_urls()
    filename = create_csv('my_csv')
    for url in urls:
        general_tournament_data(url, filename)

    get_players_info()


if __name__ == '__main__':
    main()