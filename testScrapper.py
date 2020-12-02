from AtpScrapper import AtpScrapper, read_urls

filtre = 'url'
start_year = 2000
end_year = 2001
urls = read_urls(start_year, end_year, filtre)
x = AtpScrapper(filtre)






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