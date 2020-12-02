from atpScrapper import atpScrapper

def get_tournament_tr():
    url = 'https://www.atptour.com/en/scores/results-archive?year=2000'
    x = atpScrapper()
    driver = x._connexion(url)







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