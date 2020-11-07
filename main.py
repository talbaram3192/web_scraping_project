from scrap_general import *
from scrap_scores import *


def extract_urls(urls, name):
    """ extract tournaments data from all URLS in a list given and save on a csv file """
    if name == 'tournament':
        filename = create_csv(name, COLUMNS)  # create csv file
        for url in urls:
            general_tournament_data(url,filename)
    elif name == 'tournament_scores':
        filename = create_csv(name, COLUMNS)
        pass


def main():
    name = input('What data do you want to extract? tournament or tournament_scores ')
    while name not in ['tournament', 'tournament_scores']:
        name = input('What data do you want to extract? Tournament or Tournament_scores ')
    if name == 'tournament':
        print('Extracting general tournament data')
        extract_urls(read_urls(), name)
    else :
        print('Extracting score tournament data')
        extract_scores()


if __name__ == '__main__':
    main()
