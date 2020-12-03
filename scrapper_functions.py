import argparse


def read_urls(start_year, finish_year, filter):
    """ read all relevant URLS from the ATP website and return a list of them """
    url_base = 'https://www.atptour.com/en/scores/results-archive?year='
    urls = list()
    year = start_year         # get all URL pages starting from the chosen year
    while year <= finish_year:  # stop collecting URLS when reaching chosen 'finish_year'
        urls.append(url_base+str(year))
        year += 1
    return urls


def scrapper_parser():
    """ Generate a parser for the scrapper. """
    parser = argparse.ArgumentParser()

    parser.add_argument('start_year', type=int, help="The script will start scraping from this year")
    parser.add_argument('end_year', type=int, help="The script will finish scraping at this year",
                        nargs='?', default=2020)
    parser.add_argument('filter', choices=['atpgs', 'gs', 'atp', '1000', "ch", "fu", "XXI"],
                        nargs='?', default='atpgs',
                        help="Filter for the search: "
                             "all- search all tournaments. "
                             "atpgs- ATP Tour & Grand Slams "
                             "gs - Grand Slams"
                             "atp- search only atp tournaments. "
                             "1000- atp1000. "
                             "ch - ATP Challenger Tour"
                             "fu - ITF Future"
                             "XXI - XXI")
    parser.add_argument("-p", "--player", choices=['winners', 'all'],
                        help="Scrap winners information")
    parser.add_argument("-s", "--scores", help="Scrap scores of each match in a tournament",
                        action='store_true')
    return parser

