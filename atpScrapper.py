from selenium import webdriver, common
import argparse
import players_profile
import mysql.connector
import config

def general_tournament_data(url, filter):
    """
    Extract general information about tournament of a particular year from ATP
    """
    driver = webdriver.Chrome(config.PATH)
    driver.get(url)
    year = int(url.split('=')[1])
    print(f"scraping results from year {year}..")
    table = driver.find_element_by_id('scoresResultsArchive')
    tbody = table.find_element_by_tag_name('tbody')
    tr = tbody.find_elements_by_tag_name('tr')
    config.logging.info(f'Scraping results from year {url}. scraping {filter} tournaments.')

    for i in tr:  # each 'tr' tag holds the relevant information regarding each tournament in the URL

        try:    # find which type of tournament it is- 250, 500, 1000, grand slam, finals?
            td_class = i.find_element_by_class_name('tourney-badge-wrapper')
            tourn_type = td_class.find_element_by_tag_name('img').get_attribute('src')
            new_tourn_type = tourn_type.split('_')[1].split('.')[0]
        except common.exceptions.NoSuchElementException:
            new_tourn_type = 'NA'
            config.logging.warning("Couldn't find tournament's type")

        # check if tournament exists in DB

        td_content = i.find_element_by_class_name('title-content')  # basic details- name, location and dates
        name = td_content.find_element_by_class_name('tourney-title').text  # tournament's name
        cursor = config.CON.cursor()
        cursor.execute("select * from tournaments where name = %s "
                       "and year = %s ", [name, year])  # check if tournament exist in DB,
        check_exist = cursor.fetchall()
        if len(check_exist) == 0:   # if tournament doesnt exist
            if filter == new_tourn_type or filter == 'all':
                config.logging.info(f'Scraping tournament of type: {new_tourn_type}')

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
                    config.logging.error("couldn't get tournament's prize money")

                td_winners = i.find_elements_by_class_name('tourney-details')[3]  # winners
                winners = td_winners.find_elements_by_class_name('tourney-detail-winner')
                url_tournament = extract_url_result(i)

                # get the tournament winners:
                winners_list = list()
                if len(winners) == 1:  # one winner- either singles, doubles or team
                    if winners[0].text[:3] == 'SGL':
                        try:  # get players links to profiles
                            winner_profile = winners[0].find_element_by_tag_name('a').get_attribute('href')
                            winners_list.append(players_profile.get_players_info(winner_profile))
                            config.logging.info(f"Scraped winner's profile- {winner_profile} successfully!!")
                        except common.exceptions.NoSuchElementException:
                            config.logging.error("couldn't get winner's profile")   # link doesn't exist
                        except IndexError:
                            config.logging.error("couldn't get winner's profile")
                    elif winners[0].text[:3] == 'DBL':
                        try:     # get players links to profiles
                            a_tags = winners[0].find_elements_by_tag_name('a')
                            for a in a_tags:
                                winners_list.append(players_profile.get_players_info(a.get_attribute('href')))
                                config.logging.info(f"Scraped winner's profile- {a.get_attribute('href')} successfully!!")
                        except common.exceptions.NoSuchElementException:
                            config.logging.error("couldn't get winner's profile")  # link doesn't exist
                        except IndexError:
                            config.logging.error("couldn't get winner's profile")
                    else:
                        try:
                            winners_team = winners[0].text[6:]   # teams don't have profiles so there's no links to add
                            config.logging.info(f"Scraped team's profile- {winners_team} successfully!!")
                        except common.exceptions.NoSuchElementException:
                            config.logging.error("couldn't get team's profile")  # link doesn't exist
                        except IndexError:
                            config.logging.error("couldn't get team's profile")

                        # TODO add team to teams db and to winners_list..
                        # TODO add tour finals as option in the beginning..??
                        # TODO divide into another page..??
                        # TODO add type of winner to champions


                else:  # len=3. two types of winners- singles and doubles (there are no tournaments that include
                    for winner in winners:  # singles, doubles and team winners)
                        if winner.text[:3] == 'SGL':
                            try:   # get players links to profiles
                                winner_profile = winner.find_element_by_tag_name('a').get_attribute('href')
                                winners_list.append(players_profile.get_players_info(winner_profile))
                                config.logging.info(f"Scraped winner's profile- {winner_profile} successfully!!")
                            except common.exceptions.NoSuchElementException:
                                config.logging.error("couldn't get winner's profile")  # link doesn't exist
                            except IndexError:
                                config.logging.error("couldn't get winner's profile")
                        else:
                            try:   # get players links to profiles
                                a_tags = winner.find_elements_by_tag_name('a')
                                for a in a_tags:
                                    winners_list.append(players_profile.get_players_info(a.get_attribute('href')))
                                    config.logging.info(f"Scraped winner's profile- {a.get_attribute('href')} successfully!!")
                            except common.exceptions.NoSuchElementException:
                                config.logging.error("couldn't get winner's profile")  # link doesn't exist
                            except IndexError:
                                config.logging.error("couldn't get winner's profile")

                try:
                    cursor.execute(''' insert into tournaments (year,type,name,location,date,SGL_draw,
                        DBL_draw, surface, prize_money) values(%s,%s,%s,%s,%s,%s,%s,%s,%s) ''', [year, new_tourn_type,
                                                                                                  name, location, dates,
                                                                                                  draw_singles,
                                                                                                 draw_doubles,
                                                                                                 surface, prize_money])
                    config.logging.info(f"Scraped tournament {name} - {year} and updated DB successfully!")

                    # enter tournament and winner to 'champions' table
                    cursor.execute("select tournament_id from tournaments where name = %s and"
                                   " year = %s", [name, year])
                    tourn_id = cursor.fetchall()
                    for winner in winners_list:
                        try:
                            cursor.execute(''' insert into champions(winner_id, tournament_id)
                                            values(%s, %s)''', [winner[0][0], tourn_id[0][0]])
                            config.logging.info(f'Inserted champions to tournament- {name} successfully!')

                        except (mysql.connector.IntegrityError, mysql.connector.DataError) as e:
                            config.logging.error(f'Error when trying to insert champions to'
                                                 f' tournament- {name}: {e}')

                except (mysql.connector.IntegrityError, mysql.connector.DataError) as e:
                    config.logging.error(f'Error when trying to insert tournament- {name}: {e}')

                config.CON.commit()

        else:
            config.logging.info(f'''This tournament: {name} - {year} was already scraped before, and is '
                            already located in the DB''')

    driver.close()
    config.logging.info(f'Finished scraping {url}')


def read_urls(start_year, finish_year, filter):
    """ read all relevant URLS from the ATP website and return a list of them """
    url_base = 'https://www.atptour.com/en/scores/results-archive?year={}&tournamentType={}'
    urls = list()
    year = start_year         # get all URL pages starting from the chosen year
    while year <= finish_year:  # stop collecting URLS when reaching chosen 'finish_year'
        urls.append(url_base.format(year,filter))
        year += 1
    return urls


class AtpScrapper:

    def __init__(self,new_tourn_type):
        self.year = None
        self.location = None
        self.date = None
        self.name = None
        self.draw_singles = None
        self.new_tourn_type = new_tourn_type
        self.draw_doubles= None
        self.surface = None
        self.prize_money = None
        self.url_tournament = None

    def _connexion(self,url):
        """ return a selenium object containing the page of the input url."""
        driver = webdriver.Chrome(config.PATH)
        driver.get(url)
        year = int(url.split('=')[1])
        print(f"scraping results from year {year}..")
        return driver

    def _set_tournament_type(self, selenium_obj):
        """ Output the tournament type from a selenium object input"""
        try:  # find which type of tournament it is- 250, 500, 1000, grand slam, finals?
            td_class = selenium_obj.find_element_by_class_name('tourney-badge-wrapper')
            tourn_type = td_class.find_element_by_tag_name('img').get_attribute('src')
            new_tourn_type = tourn_type.split('_')[1].split('.')[0]
        except common.exceptions.NoSuchElementException:
            new_tourn_type = 'NA'
            config.logging.warning("Couldn't find tournament's type")
        self.new_tourn_type = new_tourn_type

    def _set_tournament_title_content(self, selenium_object):
        """ Set the name, location and date of the tournament from a selenium object input ('title-content') """
        td_content = selenium_object.find_element_by_class_name('title-content')  # basic details- name, location,dates
        self.name = td_content.find_element_by_class_name('tourney-title').text  # tournament's name
        self.location = td_content.find_element_by_class_name('tourney-location').text  # tournament's location
        self.dates = td_content.find_element_by_class_name('tourney-dates').text  # tournament's dates

    def _set_tournament_detail(self, selenium_object):
        """ Set draw_singles, doubles, and surface, prize_money from a selenium object input ('tourney-detail)"""
        td_draw = selenium_object.find_elements_by_class_name('tourney-details')  # number of participants in the draw
        self.draw_singles = int(td_draw[0].find_elements_by_tag_name('span')[0].text)  # singles- draw
        self.draw_doubles = int(td_draw[0].find_elements_by_tag_name('span')[1].text)  # doubles- draw
        self.surface = td_draw[1].text  # surface type
        try:
            self.prize_money = int(td_draw[2].text[2:].replace(',', ''))  # prize money
        except:
            self.prize_money = None
            config.logging.error("couldn't get tournament's prize money")

    def _set_url_scores(self, selenium_object):
        """
        Takes a selenium class object (selenium.webdriver.remote.webelement.WebElement) of an atp website and extract
        the url to a webpage with detail results of each tournament. Return NA if it does not find the tag.
        """
        try:
            self.url_tournament = selenium_object.find_element_by_class_name('button-border').get_attribute('href')
        except common.exceptions.NoSuchElementException:
            self.url_tournament = 'NA'

    def tournament_data(self, url):
        table = self._connexion(url).find_element_by_id('scoresResultsArchive')
        tr = table.find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')
        # config.logging.info(f'Scraping results from year {url}. scraping {filter} tournaments.')
        for i in tr:  # each 'tr' tag holds the relevant information regarding each tournament in the URL
            if self.new_tourn_type is None:
                self._set_tournament_type(i)  # Tournament Type
            self._set_tournament_title_content(i)  # Set name, location, dates from title-content

            # check if tournament exists in DB

            cursor = config.CON.cursor()
            cursor.execute("select * from tournaments where name = %s "
                           "and year = %s ", [self.name, self.year])  # check if tournament exist in DB,
            check_exist = cursor.fetchall()
            if len(check_exist) > 0:  # if tournament does exist
                config.logging.info(f'''This tournament: {self.name} - {self.year} was already scraped before, and is '
                                already located in the DB''')
                break

            config.logging.info(f'Scraping tournament of type: {self.new_tourn_type}')
            self._set_tournament_detail(i)  # Set draw, single, double, surface and prize_money
            self._set_url_scores(i) # Set url of tournament scores


            td_winners = i.find_elements_by_class_name('tourney-details')[3]  # winners
            winners = td_winners.find_elements_by_class_name('tourney-detail-winner')


            # get the tournament winners:
            winners_list = list()
            if len(winners) == 1:  # one winner- either singles, doubles or team
                if winners[0].text[:3] == 'SGL':
                    try:  # get players links to profiles
                        winner_profile = winners[0].find_element_by_tag_name('a').get_attribute('href')
                        winners_list.append(players_profile.get_players_info(winner_profile))
                        config.logging.info(f"Scraped winner's profile- {winner_profile} successfully!!")
                    except common.exceptions.NoSuchElementException:
                        config.logging.error("couldn't get winner's profile")  # link doesn't exist
                    except IndexError:
                        config.logging.error("couldn't get winner's profile")
                elif winners[0].text[:3] == 'DBL':
                    try:  # get players links to profiles
                        a_tags = winners[0].find_elements_by_tag_name('a')
                        for a in a_tags:
                            winners_list.append(players_profile.get_players_info(a.get_attribute('href')))
                            config.logging.info(
                                f"Scraped winner's profile- {a.get_attribute('href')} successfully!!")
                    except common.exceptions.NoSuchElementException:
                        config.logging.error("couldn't get winner's profile")  # link doesn't exist
                    except IndexError:
                        config.logging.error("couldn't get winner's profile")
                else:
                    try:
                        winners_team = winners[0].text[
                                       6:]  # teams don't have profiles so there's no links to add
                        config.logging.info(f"Scraped team's profile- {winners_team} successfully!!")
                    except common.exceptions.NoSuchElementException:
                        config.logging.error("couldn't get team's profile")  # link doesn't exist
                    except IndexError:
                        config.logging.error("couldn't get team's profile")

                    # TODO add team to teams db and to winners_list..
                    # TODO add tour finals as option in the beginning..??
                    # TODO divide into another page..??
                    # TODO add type of winner to champions


            else:  # len=3. two types of winners- singles and doubles (there are no tournaments that include
                for winner in winners:  # singles, doubles and team winners)
                    if winner.text[:3] == 'SGL':
                        try:  # get players links to profiles
                            winner_profile = winner.find_element_by_tag_name('a').get_attribute('href')
                            winners_list.append(players_profile.get_players_info(winner_profile))
                            config.logging.info(f"Scraped winner's profile- {winner_profile} successfully!!")
                        except common.exceptions.NoSuchElementException:
                            config.logging.error("couldn't get winner's profile")  # link doesn't exist
                        except IndexError:
                            config.logging.error("couldn't get winner's profile")
                    else:
                        try:  # get players links to profiles
                            a_tags = winner.find_elements_by_tag_name('a')
                            for a in a_tags:
                                winners_list.append(players_profile.get_players_info(a.get_attribute('href')))
                                config.logging.info(
                                    f"Scraped winner's profile- {a.get_attribute('href')} successfully!!")
                        except common.exceptions.NoSuchElementException:
                            config.logging.error("couldn't get winner's profile")  # link doesn't exist
                        except IndexError:
                            config.logging.error("couldn't get winner's profile")

            try:
                cursor.execute(''' insert into tournaments (year,type,name,location,date,SGL_draw,
                    DBL_draw, surface, prize_money) values(%s,%s,%s,%s,%s,%s,%s,%s,%s) ''',
                               [year, new_tourn_type,
                                name, location, dates,
                                draw_singles,
                                draw_doubles,
                                surface, prize_money])
                config.logging.info(f"Scraped tournament {name} - {year} and updated DB successfully!")

                # enter tournament and winner to 'champions' table
                cursor.execute("select tournament_id from tournaments where name = %s and"
                               " year = %s", [name, year])
                tourn_id = cursor.fetchall()
                for winner in winners_list:
                    try:
                        cursor.execute(''' insert into champions(winner_id, tournament_id)
                                        values(%s, %s)''', [winner[0][0], tourn_id[0][0]])
                        config.logging.info(f'Inserted champions to tournament- {name} successfully!')

                    except (mysql.connector.IntegrityError, mysql.connector.DataError) as e:
                        config.logging.error(f'Error when trying to insert champions to'
                                             f' tournament- {name}: {e}')

            except (mysql.connector.IntegrityError, mysql.connector.DataError) as e:
                config.logging.error(f'Error when trying to insert tournament- {name}: {e}')

            config.CON.commit()


        driver.close()
        config.logging.info(f'Finished scraping {url}')






