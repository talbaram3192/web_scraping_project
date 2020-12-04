import argparse

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
parser.add_argument("-w", "--winners", action='store_true',
                    help="Scrap winners information")
parser.add_argument("-s", "--score", help="Scrap scores of each match in a tournament and information about each"
                                          "player",
                    action='store_true')
args = parser.parse_args()
print(args)