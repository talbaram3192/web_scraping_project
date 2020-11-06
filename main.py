from scrap_general import *


def extract_urls(urls, name):
    """ extract tournaments data from all URLS in a list given and save on a csv file """

    for url in urls:
        if name == 'tournament':
            general_tournament_data(url)
        elif name == 'tournament_scores':
            pass


def main():
    name = input('What data do you want to extract? tournament or tournament_scores ')
    while name not in ['tournament', 'tournament_scores']:
        name = input('What data do you want to extract? Tournament or Tournament_scores ')
    if name == 'tournament':
        print('Extracting general tournament data')
        extract_urls(read_urls(), name)
    else :
        pass


if __name__ == '__main__':
    main()
