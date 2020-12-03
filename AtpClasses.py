from selenium import webdriver, common
import mysql.connector
import config
import re


class AtpScores:
    def __init__(self):
        self._driver = None
        self.url = None
        self.score = None
        self.winner = None
        self.loser = None
        self.round = None
        self.url_winner = None
        self.url_loser = None

    def scores_tournament_data(self, atp_info):
        """
        Extract general information about tournament of a particular year from ATP
        """
        atp_table = []
        # start_time = time.time()
        name, year, url = atp_info[0], atp_info[1], atp_info[2]
        driver = webdriver.Chrome(PATH)
        driver.get(url)
        # Count the number of KOs
        KO_count = 0

        try:
            table = driver.find_element_by_class_name('day-table')
            tbody = table.find_elements_by_tag_name('tbody')
            thead = table.find_elements_by_tag_name('thead')
            for head, body in zip(thead, tbody):
                winner = winner_url = loser = loser_url = score = url_detail = url_check = None
                rounds = head.find_element_by_tag_name('th').text
                tr_l = body.find_elements_by_tag_name('tr')
                for tr in tr_l:
                    winner = tr.find_elements_by_class_name('day-table-name')[0].text
                    winner_url = tr.find_elements_by_class_name('day-table-name')[0] \
                        .find_element_by_tag_name('a').get_attribute('href')
                    loser = tr.find_elements_by_class_name('day-table-name')[1].text
                    loser_url = tr.find_elements_by_class_name('day-table-name')[1] \
                        .find_element_by_tag_name('a').get_attribute('href')
                    score = tr.find_element_by_class_name('day-table-score').text
                    url_detail = tr.find_element_by_class_name('day-table-button') \
                        .find_element_by_tag_name('a').get_attribute('href')
                    url_check = 'OK'
                    new_row = [name, year, url, rounds, loser, winner, score, url_detail,
                               winner_url, loser_url, url_check]
                    # We write the new line into the csv
                    writer.writerow(new_row)
        except common.exceptions.NoSuchElementException:
            url_check = 'KO'
            KO_count += 1
            writer.writerow([name, year, url, None, None, None, None, None, None, url_check])

    driver.close()


class AtpPlayer:
    def __init__(self, player_url):
        self.firstname = None
        self.lastname = None
        self.ranking_sgl = None
        self.ranking_dbl = None
        self.career_high_sgl = None
        self.career_high_dbl = None
        self.country = None
        self.date_birth = None
        self.turned_pro = None
        self.weight = None
        self.height = None
        self.total_prize_money = None
        self.player_url = player_url
        self._driver = None

    def check_player_exist(self):
        """ Check if players information exist in db. """

        self.firstname = self.player_url.split('/')[5].split('-')[0]
        self.lastname = self.player_url.split('/')[5].split('-')[1]

        # check if player exists in the DB
        cursor = config.CON.cursor()
        cursor.execute("select player_id from players where first_name = %s "
                       "and last_name = %s ", [self.firstname, self.lastname])
        check_exist = cursor.fetchall()
        if len(check_exist)>0: # Player exists in db
            config.logging.info(f"{self.firstname} {self.lastname} already exists in players table.")
            return True

    def _set_player_ranking(self):
        try:
            self.ranking_sgl = int(self._driver.find_elements_by_class_name('stat-value')[0].get_attribute(
                'data-singles'))  # current ranking- singles
            print(self.ranking_sgl)
            self.ranking_dbl = int(self._driver.find_elements_by_class_name('stat-value')[0].get_attribute(
                'data-doubles'))  # current ranking- doubles
            print(self.ranking_dbl)
        except Exception:
            ranking_sgl = None
            ranking_dbl = None
            config.logging.warning("couldn't find player's singles/doubles ranking..")

    def _set_player_highest_ranking(self):
        self.career_high_sgl = int(self._driver.find_elements_by_class_name('stat-value')[5].get_attribute(
            'data-singles'))  # career high ranking- singles
        #print(career_high_sgl)
        self.career_high_dbl = int(self._driver.find_elements_by_class_name('stat-value')[5].get_attribute(
            'data-doubles'))  # career high ranking- doubles
        #print(career_high_dbl)

    def _set_player_country(self):
        try:
            self.country = self._driver.find_element_by_class_name('player-flag-code').text  # country
            # print(self.country)
        except Exception:
            self.country = None
            config.logging.warning("couldn't find player's country..")

    def _set_player_datebirth(self):
        try:
            self.date_birth = self._driver.find_element_by_class_name('table-birthday').text.strip('()')  # date of birth
           # print(self.date_birth)
        except Exception:
            self.date_birth = None
            config.logging.warning("couldn't find player's date of birth..")

    def _set_player_turnedpro(self):
        try:
            self.turned_pro = int(self._driver.find_elements_by_class_name('table-big-value')[1].text)  # turned pro
            # print(self.turned_pro)
        except Exception:
            self.turned_pro = None
            config.logging.warning("couldn't find the date the player turned pro..")

    def _set_player_weight_height(self):
        try:
            self.weight = float(self._driver.find_element_by_class_name('table-weight-lbs').text)  # weight
            #print(self.weight)

            self.height = float(self._driver.find_element_by_class_name('table-height-cm-wrapper').text[1:4])  # height
            # print(self.height)
        except Exception:
            self.weight = None
            self.height = None
            config.logging.warning("couldn't find player's height\weight..")

    def _set_player_total_prize(self):
        try:
            self.total_prize_money = int(
                self._driver.find_elements_by_class_name('stat-value')[8].text.split()[0][1:].replace(',',
                                                                                                ''))  # total prize money
           # print(self.total_prize_money)
        except Exception:
            self.total_prize_money = None
            config.logging.warning("couldn't find player's total prize money earnings..")

    def get_player_info(self):
        """ Get players information from their profiles """

        # check if player exists in the DB
        if self.check_player_exist(): return self # if player does exist in DB
        # connect to ChromeDriver
        driver = webdriver.Chrome(config.PATH)
        driver.get(self.player_url)
        self._driver = driver

        self._set_player_ranking() # Player ranking
        self._set_player_highest_ranking() # Player highest ranking
        self._set_player_country() # Player country
        self._set_player_datebirth() # Player date of birth
        self._set_player_turnedpro() # Player turned pro
        self._set_player_weight_height() # Player weight height
        self._set_player_total_prize() # Player total_prize
        self._driver.close()
        return self


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
        self.single_winner = None
        self.double_winner = None
        self._driver = None
        self._url_single_winner = None
        self.players = None

    def _connexion(self, url):
        """ return a selenium object containing the page of the input url."""
        driver = webdriver.Chrome(config.PATH)
        driver.get(url)
        year = re.findall(r'year=([0-9]{4})', url)[0]
        self.year = year
        print(f"scraping results from year {year}..")
        self._driver = driver

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
            self.prize_money = int(td_draw[2].text[1:].replace(',', ''))  # prize money
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

    def _set_winner(self, selenium_object):
        """ Set winner from selenium object - (tourney-detail-winner)"""
        winners = selenium_object.find_elements_by_class_name('tourney-detail-winner') # winners
        # get the tournament winners:
        for winner in winners:
            if 'SGL: ' in winner.text:
                self.single_winner = winner.text.split(': ')[1]
                self._url_single_winner = winner.find_element_by_tag_name('a').get_attribute('href')
            elif 'DBL: ' in winner.text:
                self.double_winner = winner.text.split(': ')[1]

    def _save_into_database(self, player=None):
        """Save tournament information in tournament table inside web_scraping_project"""
        cursor = config.CON.cursor()
        idplayer = 'NA'
        if player is not None: check_exist = player.check_player_exist()
        if (self.players == 'winners') & (check_exist is None): # player is not in DB
            try:
                cursor.execute(''' insert into players (first_name,last_name,ranking_DBL,ranking_SGL,
                career_high_DBL,career_high_SGL,turned_pro, weight,height, total_prize_money, country, birth)
                values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ''',
                               [player.firstname, player.lastname,
                                player.ranking_dbl, player.ranking_sgl, player.career_high_dbl,
                                player.career_high_sgl, player.turned_pro, player.weight, player.height,
                                player.total_prize_money, player.country, player.date_birth])
                config.logging.info(f"Added {player.firstname} {player.lastname} into the DB")
                idplayer = cursor.lastrowid
                config.CON.commit()
            except (mysql.connector.IntegrityError, mysql.connector.DataError) as e:
                config.logging.error(f"Failed to enter player {player.firstname} {player.lastname} details into the DB- {e}")
        elif (self.players == 'winners') & (check_exist):  # Player is already in db
            cursor.execute("select player_id from players where first_name = %s "
                           "and last_name = %s ", [player.firstname, player.lastname])
            idplayer = cursor.fetchall()[0][0]
            # print('idplayer' : idplayer)
        try:
            cursor.execute(''' insert into tournaments (year,type,name,location,date,SGL_draw,
                DBL_draw, surface, prize_money, single_winner, double_winner, winner_single_id) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ''',
                           [self.year, self.new_tourn_type,
                            self.name, self.location, self.dates,
                            self.draw_singles,
                            self.draw_doubles,
                            self.surface, self.prize_money,
                            self.single_winner, self.double_winner,
                            idplayer])
            config.logging.info(f"Scraped tournament {self.name} - {self.year} and updated DB successfully!")
        except (mysql.connector.IntegrityError, mysql.connector.DataError) as e:
            config.logging.error(f'Error when trying to insert tournament- {self.name}: {e}')

        config.CON.commit()
        cursor.close()

    def _check_tournament_exist(self):
        """ check if tournament exists in DB  """

        cursor = config.CON.cursor()
        cursor.execute("select * from tournaments where name = %s "
                       "and year = %s ", [self.name, self.year])  # check if tournament exist in DB,
        check_exist = cursor.fetchall()
        cursor.close()
        if len(check_exist) > 0:  # if tournament does exist
            config.logging.info(f'''This tournament: {self.name} - {self.year} was already scraped before, and is '
                                        already located in the DB''')
            return True

    def tournament_data(self, url, score=None, players=None):
        """Go through the url page, get information on each tournament and save them in tournament table inside
        web_scraping_project db
        url - url to scrap
        score = if True scrap all scores of each tournament
        players - if 'winner' scrap information about winners of each tournament.
                  if 'all' scrap information about each player of the tournament
                """
        player = None
        self.players = players
        self._connexion(url)
        table = self._driver.find_element_by_id('scoresResultsArchive')
        tr = table.find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')
        # config.logging.info(f'Scraping results from year {url}. scraping {filter} tournaments.')
        for i in tr:  # each 'tr' tag holds the relevant information regarding each tournament in the URL
            if self.new_tourn_type is None:
                self._set_tournament_type(i)  # Tournament Type
            self._set_tournament_title_content(i)  # Set name, location, dates from title-content
            # Check if tournament exists in db:
            if self._check_tournament_exist():
                break
            config.logging.info(f'Scraping tournament of type: {self.new_tourn_type}')
            self._set_tournament_detail(i)  # Set draw, single, double, surface and prize_money
            self._set_url_scores(i) # Set url of tournament scores WE DON'T USE IT YET

            self._set_winner(i) # Set winner_single, and winner_double, if they exist
            if players == 'winners':
                player = AtpPlayer(self._url_single_winner).get_player_info()
                # Scrap winners information

            self._save_into_database(player=player)
        self._driver.close()
        config.logging.info(f'Finished scraping {url}')







