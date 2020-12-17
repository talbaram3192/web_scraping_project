from AtpClasses import AtpScrapper, AtpPlayer, AtpScores
from scrapper_functions import read_urls
import config

from selenium import webdriver, common
player_url_test = 'https://www.atptour.com/en/players/pete-sampras/s402/overview'
score_url_test = 'https://www.atptour.com/en/scores/archive/wimbledon/540/1885/results'
filtre = 'atp'
start_year = 2010
end_year = 2011
urls = read_urls(start_year, end_year, filtre)
"""
example of one tournament:
driver = webdriver.Firefox(config.PATH)
driver.get(urls[0])
table = driver.find_element_by_id('scoresResultsArchive')
tr = table.find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')
i = tr[0]
"""
player_test = AtpPlayer(player_url_test)
x = AtpScrapper(filtre)
x.tournament_data(urls[0])
score_test = AtpScores(score_url_test)
score_test.scores_tournament_data()

"""
import time
def mytimer(function):
    def wrapper(*args, **kwargs):
        timer = time.time()
        result = function(*args, **kwargs)
        timer2 = time.time() - timer
        print('Function ran in {}'.format(timer2))
    return wrapper


@mytimer
def addition(x1, x2):
    return x1, x2
"""

"""
class test:
    def __init__(self, const):
        self.id = None
        self.test = const
    def reset(self):
        self.__init__(self.test)
"""

def test_decorator(func):
    def wrapper(*args):
        try:
            x = func(*args)
        except:
            x = 'None'
            print(f'Error in {func.__name__}')
    return wrapper

@test_decorator
def division(a,b):
    print(a/b)
    return a/b

def set_decorator(func):
    def wrapper(*args):
        try:
            func()
        except Exception:
            config.logging.warning(f"Could not {func.__name__}")
def _set_player_country(self):
    try:
        self.country = self._driver.find_element_by_class_name('player-flag-code').text  # country
        # print(self.country)
    except Exception:
        self.country = None
        config.logging.warning("couldn't find player's country..")