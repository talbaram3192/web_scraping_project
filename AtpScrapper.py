from selenium import webdriver, common
import argparse
import players_profile
import mysql.connector
import config
import re
import pandas as pd


def read_urls(start_year, finish_year, filter):
    """ read all relevant URLS from the ATP website and return a list of them """
    url_base = 'https://www.atptour.com/en/scores/results-archive?year={}&tournamentType={}'
    urls = list()
    year = start_year         # get all URL pages starting from the chosen year
    while year <= finish_year:  # stop collecting URLS when reaching chosen 'finish_year'
        urls.append(url_base.format(year, filter))
        year += 1
    return urls


class AtpScrapper:

    def __init__(self,new_tourn_type):
        self.year = None
        self.location = None
        self.date = None
        self.name = None
        self.draw_singles = None
        self.new_tourn_type = new_tourn_type
        self.draw_doubles= None
        self.surface = None
        self.prize_money = None
        self.url_tournament = None
        self.single_winner = None
        self.double_winner = None
        self._driver = None

    def _connexion(self,url):
        """ return a selenium object containing the page of the input url."""
        driver = webdriver.Chrome(config.PATH)
        driver.get(url)
        year = re.findall(r'year=([0-9]{4})', url)[0]
        print(f"scraping results from year {year}..")
        self._driver = driver

    def _set_tournament_type(self, selenium_obj):
        """ Output the tournament type from a selenium object input"""
        try:  # find which type of tournament it is- 250, 500, 1000, grand slam, finals?
            td_class = selenium_obj.find_element_by_class_name('tourney-badge-wrapper')
            tourn_type = td_class.find_element_by_tag_name('img').get_attribute('src')
            new_tourn_type = tourn_type.split('_')[1].split('.')[0]
        except common.exceptions.NoSuchElementException:
            new_tourn_type = 'NA'
            config.logging.warning("Couldn't find tournament's type")
        self.new_tourn_type = new_tourn_type

    def _set_tournament_title_content(self, selenium_object):
        """ Set the name, location and date of the tournament from a selenium object input ('title-content') """
        td_content = selenium_object.find_element_by_class_name('title-content')  # basic details- name, location,dates
        self.name = td_content.find_element_by_class_name('tourney-title').text  # tournament's name
        self.location = td_content.find_element_by_class_name('tourney-location').text  # tournament's location
        self.dates = td_content.find_element_by_class_name('tourney-dates').text  # tournament's dates

    def _set_tournament_detail(self, selenium_object):
        """ Set draw_singles, doubles, and surface, prize_money from a selenium object input ('tourney-detail)"""
        td_draw = selenium_object.find_elements_by_class_name('tourney-details')  # number of participants in the draw
        self.draw_singles = int(td_draw[0].find_elements_by_tag_name('span')[0].text)  # singles- draw
        self.draw_doubles = int(td_draw[0].find_elements_by_tag_name('span')[1].text)  # doubles- draw
        self.surface = td_draw[1].text  # surface type
        try:
            self.prize_money = int(td_draw[2].text[2:].replace(',', ''))  # prize money
        except:
            self.prize_money = None
            config.logging.error("couldn't get tournament's prize money")

    def _set_url_scores(self, selenium_object):
        """
        Takes a selenium class object (selenium.webdriver.remote.webelement.WebElement) of an atp website and extract
        the url to a webpage with detail results of each tournament. Return NA if it does not find the tag.
        """
        try:
            self.url_tournament = selenium_object.find_element_by_class_name('button-border').get_attribute('href')
        except common.exceptions.NoSuchElementException:
            self.url_tournament = 'NA'

    def _set_winner(self, selenium_object):
        """ Set winner from selenium object - (tourney-detail-winner)"""
        winners = selenium_object.find_elements_by_class_name('tourney-detail-winner') # winners

        # get the tournament winners:
        for winner in winners:
            if 'SGL: ' in winner.text:
                self.single_winner = winner.text.split(': ')[1]
            elif 'DBL: ' in winner.text:
                self.double_winner = winner.text.split(': ')[1]

    def _save_into_database(self):
        cursor = config.CON.cursor()
        try:
            cursor.execute(''' insert into tournaments (year,type,name,location,date,SGL_draw,
                DBL_draw, surface, prize_money, single_winner, double_winner) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ''',
                           [self.year, self.new_tourn_type,
                            self.name, self.location, self.dates,
                            self.draw_singles,
                            self.draw_doubles,
                            self.surface, self.prize_money,
                            self.single_winner, self.double_winner])
            config.logging.info(f"Scraped tournament {self.name} - {self.year} and updated DB successfully!")
        except (mysql.connector.IntegrityError, mysql.connector.DataError) as e:
            config.logging.error(f'Error when trying to insert tournament- {self.name}: {e}')

        config.CON.commit()
        cursor.close()

    def tournament_data(self, url):
        self._connexion(url)
        table = self._driver.find_element_by_id('scoresResultsArchive')
        tr = table.find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')
        # config.logging.info(f'Scraping results from year {url}. scraping {filter} tournaments.')
        for i in tr:  # each 'tr' tag holds the relevant information regarding each tournament in the URL
            if self.new_tourn_type is None:
                self._set_tournament_type(i)  # Tournament Type
            self._set_tournament_title_content(i)  # Set name, location, dates from title-content

            # check if tournament exists in DB

            cursor = config.CON.cursor()
            cursor.execute("select * from tournaments where name = %s "
                           "and year = %s ", [self.name, self.year])  # check if tournament exist in DB,
            check_exist = cursor.fetchall()
            cursor.close()
            if len(check_exist) > 0:  # if tournament does exist
                config.logging.info(f'''This tournament: {self.name} - {self.year} was already scraped before, and is '
                                already located in the DB''')
                break

            config.logging.info(f'Scraping tournament of type: {self.new_tourn_type}')
            self._set_tournament_detail(i)  # Set draw, single, double, surface and prize_money
            self._set_url_scores(i) # Set url of tournament scores
            self._set_winner(i) # Set winner_single, and winner_double, if they exist
            self._save_into_database()
        self._driver.close()
        config.logging.info(f'Finished scraping {url}')






