from AtpClasses import AtpScrapper, AtpPlayer
from scrapper_functions import read_urls
player_url_test = 'https://www.atptour.com/en/players/pete-sampras/s402/overview'
filtre = 'url'
start_year = 2000
end_year = 2001
urls = read_urls(start_year, end_year, filtre)
player_test = AtpPlayer(player_url_test)
x = AtpScrapper(filtre)
print(urls[0])
x.tournament_data(urls[0], players='winners')


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