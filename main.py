import config
from scrapper_functions import read_urls, scrapper_parser
from AtpClasses import AtpScrapper


def main():
    # parser
    parser = scrapper_parser()
    args = parser.parse_args()

    urls = read_urls(args.start_year, args.end_year, args.filter)  # get all tournament's URLs between specified years
    scrapper = AtpScrapper(args.filter)
    # General Tournament Scrapper
    for url in urls:
        config.logging.info('Started scraping!')
        scrapper.tournament_data(url, score=args.score, players=args.players)     # scrape tournament's details based on given filters

    config.logging.info('Finished Scraping successfully!')


if __name__ == '__main__':
    main()