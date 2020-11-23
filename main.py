import requests
from selenium import webdriver, common
import argparse
import players_profile
import mysql.connector

CON = mysql.connector.connect(port='3307', user='root', password='Twtcmss2954455'
                              , db='web_scraping_project')


PATH = 'C:\Program Files\chromedriver.exe'
# COLUMNS = ['Year', 'Name', 'Location', 'Dates', 'Draw- singles', 'Draw- doubles', 'Surface', 'Prize money',
#            'Winner- singles', 'Winner- doubles', 'Winner- team', 'Tournament url']
# PLAYERS = list()


def read_urls(start_year, finish_year):
    """ read all relevant URLS from the ATP website and return a list of them """
    url_base = 'https://www.atptour.com/en/scores/results-archive?year='
    urls = list()
    year = start_year         # get all URL pages starting from the chosen year
    while year <= finish_year:  # stop collecting URLS when reaching chosen 'finish_year'
        urls.append(url_base+str(year))
        year += 1
    return urls


def extract_url_result(webelement_atp):
    """
    Takes a selenium class object (selenium.webdriver.remote.webelement.WebElement) of an atp website and extract
    the url to a webpage with detail results of each tournament. Return NA if it does not find the tag.
    """
    try:
        return webelement_atp.find_element_by_class_name('button-border').get_attribute('href')
    except common.exceptions.NoSuchElementException:
        return 'NA'


def general_tournament_data(url, filter):
    """
    Extract general information about tournament of a particular year from ATP
    """
    driver = webdriver.Chrome(PATH)
    driver.get(url)
    year = int(url.split('=')[1])
    print(f"scraping results from year {year}..")
    table = driver.find_element_by_id('scoresResultsArchive')
    tbody = table.find_element_by_tag_name('tbody')
    tr = tbody.find_elements_by_tag_name('tr')

    for i in tr:  # each 'tr' tag holds the relevant information regarding each tournament in the URL

        try:    # find which type of tournament it is- 250, 500, 1000, grand slam, finals?
            td_class = i.find_element_by_class_name('tourney-badge-wrapper')
            tourn_type = td_class.find_element_by_tag_name('img').get_attribute('src')
            new_tourn_type = tourn_type.split('_')[1].split('.')[0]
        except common.exceptions.NoSuchElementException:
            new_tourn_type = 'NA'

        # check if tournament exists in DB

        td_content = i.find_element_by_class_name('title-content')  # basic details- name, location and dates
        name = td_content.find_element_by_class_name('tourney-title').text  # tournament's name
        cursor = CON.cursor()
        cursor.execute("select * from tournaments where name = %s "
                       "and year = %s ", [name, year])  # check if tournament exist in DB,
        check_exist = cursor.fetchall()
        if len(check_exist) == 0:   # if tournament doesnt exist
            if filter == new_tourn_type or filter == 'all':

                location = td_content.find_element_by_class_name('tourney-location').text  # tournament's location
                dates = td_content.find_element_by_class_name('tourney-dates').text  # tournament's dates

                td_draw = i.find_elements_by_class_name('tourney-details')[0]  # number of participants in the draw
                draw_singles = int(td_draw.find_elements_by_tag_name('span')[0].text) # singles- draw
                draw_doubles = int(td_draw.find_elements_by_tag_name('span')[1].text)  # doubles- draw

                surface = i.find_elements_by_class_name('tourney-details')[1].text  # surface type

                try:
                    prize_money = i.find_elements_by_class_name('tourney-details')[2].text[1:].replace(',', '')
                    if prize_money != '' and prize_money[1].isalpha():
                        prize_money = int(i.find_elements_by_class_name('tourney-details')[2].text[2:].replace(',', ''))  # prize money
                    else:
                        prize_money = int(i.find_elements_by_class_name('tourney-details')[2].text[2:].replace(',', ''))
                except Exception:
                    prize_money = None

                td_winners = i.find_elements_by_class_name('tourney-details')[3]  # winners
                winners = td_winners.find_elements_by_class_name('tourney-detail-winner')
                url_tournament = extract_url_result(i)

                # get the tournament winners:
                if len(winners) == 1:  # one winner- either singles, doubles or team
                    if winners[0].text[:3] == 'SGL':
                        try:  # get players links to profiles
                            winner_profile = winners[0].find_element_by_tag_name('a').get_attribute('href')
                            players_profile.get_players_info(winner_profile)
                        except common.exceptions.NoSuchElementException:
                            pass   # link doesn't exist
                        except IndexError:
                            pass
                    elif winners[0].text[:3] == 'DBL':
                        try:     # get players links to profiles
                            a_tags = winners[0].find_elements_by_tag_name('a')
                            for a in a_tags:
                                players_profile.get_players_info(a.get_attribute('href'))
                        except common.exceptions.NoSuchElementException:
                            pass  # link doesn't exist
                        except IndexError:
                            pass
                    else:
                        try:
                            winners_team = winners[0].text[6:]   # teams dont have profiles so there's no links to add
                        except common.exceptions.NoSuchElementException:
                            pass  # link doesn't exist
                        except IndexError:
                            pass
                                                             # in this case
                        # TODO: add team to teams db
                        # TODO: organize the exeptions normally
                        # TODO: delete 'None' when not needed..
                        # TODO: edit tournaments date's
                        # TODO: add logging
                        # TODO: add tour finals

                else:  # len=3. two types of winners- singles and doubles (there are no tournaments that include
                    for winner in winners:  # singles, doubles and team winners)
                        if winner.text[:3] == 'SGL':
                            try:   # get players links to profiles
                                winner_profile = winner.find_element_by_tag_name('a').get_attribute('href')
                                players_profile.get_players_info(winner_profile)
                            except common.exceptions.NoSuchElementException:
                                pass  # link doesn't exist
                            except IndexError:
                                pass
                        else:
                            try:   # get players links to profiles
                                a_tags = winner.find_elements_by_tag_name('a')
                                for a in a_tags:
                                    players_profile.get_players_info(a.get_attribute('href'))
                            except common.exceptions.NoSuchElementException:
                                pass  # link doesn't exist
                            except IndexError:
                                pass

                cursor.execute(''' insert into tournaments (year,type,name,location,date,SGL_draw,
                    DBL_draw, surface, prize_money) values(%s,%s,%s,%s,%s,%s,%s,%s,%s) ''', [year, new_tourn_type,
                                                                                              name, location, dates,
                                                                                              draw_singles, draw_doubles,                                                                        surface, prize_money])
                CON.commit()

    driver.close()


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('start_year', type=int, help="The script will start scraping from this year")
    parser.add_argument('end_year', type=int, help="The script will finish scraping at this year")
    parser.add_argument('filter', choices=['all', '250', '500', '1000', 'grandslam'],
                        help="Filter for the search: "
                             "all- search all tournaments. "
                             "250- search only atp250 tournaments. "
                             "500- search only atp500 tournaments. "
                             "1000- search only atp1000 tournaments. "
                             "grand_slam- search only grand slam tournaments")

    args = parser.parse_args()

    urls = read_urls(args.start_year, args.end_year)  #get all tournament's URLs between specified years

    for url in urls:
        general_tournament_data(url, args.filter)     #scrape tournament's details based on given filters


if __name__ == '__main__':
    main()