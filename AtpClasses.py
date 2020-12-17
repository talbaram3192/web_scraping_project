from selenium import webdriver, common
import mysql.connector
import config
import re
import json


class API():
    def __init__(self):
        self._conn = config.api_conn
        self._conn2 = None
        self._rankings = None
        self._meetings = None
        self.player_1_id = None
        self.player_2_id = None
        self.same_winner = None
        self.round = None
        self.tourn_name = None
        self.venue = None

    def get_all_players(self):
        """ Get rankings of all players- get their ID's"""
        config.connect(self._conn)
        res = self._conn.getresponse()
        data = res.read()
        data_dec = json.loads(data.decode("utf-8"))
        self._rankings = data_dec['rankings'][1]['player_rankings']

    def getLastMeeting(self):
        self._conn2 = config.api_conn2
        config.connect2(self._conn2, self.player_1_id, self.player_2_id)
        res2 = self._conn2.getresponse()
        data2 = res2.read()
        self._meetings = json.loads(data2.decode("utf-8"))

    def save_in_DB(self, game_id):
        cursor = config.CON.cursor()
        try:
            cursor.execute(''' insert into last_meeting (game_ID,round,tourn_name,venue,same_winner)
                                        values(%s,%s,%s,%s,%s)''',
                           [game_id, self.round, self.tourn_name, self.venue,
                            self.same_winner])
            config.logging.info(f"Added last meeting details for game {game_id}")
            config.CON.commit()
        except (mysql.connector.IntegrityError, mysql.connector.DataError) as e:
            config.logging.error(f"{e}. Failed to add last meeting details for game {game_id}")
        cursor.close()

    def last_meeting(self, player_1, player_2, game_id):
        """ Get id's of two players, and then get details on their last meeting"""
        self.get_all_players()
        for i in self._rankings:
            if player_1.split()[0].lower() == i['player']['name'].split(',')[1].lower()[1:]\
                    and player_1.split()[1].lower() == i['player']['name'].split(',')[0].lower():
                self.player_1_id = i['player']['id'].split(':')[2]
            if player_2.split()[0].lower() == i['player']['name'].split(',')[1].lower()[1:]\
                    and player_2.split()[1].lower() == i['player']['name'].split(',')[0].lower():
                self.player_2_id = i['player']['id'].split(':')[2]

        if self.player_2_id != None and self.player_1_id != None:
            self.getLastMeeting()
            config.logging.info(f'IDS- {self.player_1_id, self.player_2_id}')
            self.round = self._meetings['last_meetings']['results'][0]['sport_event']['tournament_round']['name']
            self.tourn_name = self._meetings['last_meetings']['results'][0]['sport_event']['season']['name']
            self.venue = self._meetings['last_meetings']['results'][0]['sport_event_conditions']['venue']['name']
            winner = self._meetings['last_meetings']['results'][0]['sport_event_status']['winner_id'].split(':')[2]

            # Check if current winner won the last meeting as well
            if winner == self.player_1_id:
                self.same_winner = True
            else:
                self.same_winner = False

            self.save_in_DB(game_id)
        else:
            raise ValueError("Couldn't find players last meeting")


class AtpScores:
    def __init__(self, tournament):
        self._driver = None
        self._tournament = tournament
        self.url = tournament.url_score
        self.score = None
        self.winner = None
        self.winner2 = None
        self.loser = None
        self.loser2 = None
        self.round = None
        self.url_players = []
        self.teams = []
        self.url_detail = None
        self.id = None
        self._win = None
        self.doubles_scores_url = None

    def reset(self):
        """ Reset the object keeping driver and url and KO_count and round"""
        self.score = None
        self.winner = None
        self.winner2 = None
        self.loser = None
        self.loser2 = None
        self.url_players = []
        self.teams = []
        self.url_detail = None
        self.id = None
        self._win = None
        self.doubles_scores_url = None

    def _set_round(self, selenium_object):
        """ Scrap data about the score from selenium object ('head')"""
        try :
            self.round = selenium_object.find_element_by_tag_name('th').text
        except common.exceptions.NoSuchElementException:
            self.round = None

    def _set_scores_info_doubles(self, selenium_object):
        try:
            winners = selenium_object.find_elements_by_class_name('day-table-name')[0]
            a_s = winners.find_elements_by_tag_name('a')
            self.winner = a_s[0].text
            self.winner2 = a_s[1].text
            losers = selenium_object.find_elements_by_class_name('day-table-name')[1]
            a_s_l = losers.find_elements_by_tag_name('a')
            self.loser = a_s_l[0].text
            self.loser2 = a_s_l[0].text
            self.score = selenium_object.find_element_by_class_name('day-table-score').text

            # get winner's details
            for a in a_s:
                self.url_players.append((a.get_attribute('href'), 1))
            # get loser's details
            for a in a_s_l:
                self.url_players.append((a.get_attribute('href'), 0))

        except common.exceptions.NoSuchElementException:
            self.winner = self.url_winner = self.loser = self.url_loser = self.score = None

    def _set_scores_info(self, selenium_object):
        try:
            self.winner = selenium_object.find_elements_by_class_name('day-table-name')[0].text
            self.url_players.append((selenium_object.find_elements_by_class_name('day-table-name')[0] \
                .find_element_by_tag_name('a').get_attribute('href'), 1))  # URL - WINNER
            self.loser = selenium_object.find_elements_by_class_name('day-table-name')[1].text
            self.url_players.append((selenium_object.find_elements_by_class_name('day-table-name')[1] \
                .find_element_by_tag_name('a').get_attribute('href'), 0))  # Url - Losers
            self.score = selenium_object.find_element_by_class_name('day-table-score').text
            self.url_detail = selenium_object.find_element_by_class_name('day-table-button') \
                .find_element_by_tag_name('a').get_attribute('href')
        except common.exceptions.NoSuchElementException:
            self.winner = self.url_winner = self.loser = self.url_loser = self.score = self.url_detail = None

    def _check_game_exist(self):
        cursor = config.CON.cursor()
        cursor.execute(''' SELECT g.game_ID FROM games g join games_players gp on g.game_ID = gp.game_id
                            join players p on p.player_id = gp.player_id
                                WHERE tournament_id = %s AND round = %s AND p.first_name = %s 
                                AND p.last_name = %s ''',
                       [self._tournament.id, self.round, self.winner.split()[0], self.winner.split()[1]])

        check_exists = cursor.fetchall()
        if len(check_exists) > 0:
            config.logging.info(f'Round {self.round} from tournament {self._tournament.id} already exist in DB')
            cursor.close()
            return True
        else:
            cursor.close()
            return False

    def _check_game_exist_teams(self):
        cursor = config.CON.cursor()
        cursor.execute(''' SELECT g.game_ID FROM games g join games_players gp on g.game_ID = gp.game_id
                            join teams t on t.team_id = gp.team_id
                                WHERE tournament_id = %s AND round = %s AND t.name = %s ''',
                       [self._tournament.id, self.round, self.winner])

        check_exists = cursor.fetchall()
        if len(check_exists) > 0:
            config.logging.info(f'Round {self.round} from tournament {self._tournament.id} already exist in DB')
            cursor.close()
            return True
        else:
            cursor.close()
            return False

    def _save_into_games(self):
        cursor = config.CON.cursor()
        try:

            cursor.execute(''' insert into games (tournament_id,score,round)
                                values(%s,%s,%s)''',
                           [self._tournament.id, self.score,
                            self.round])
            config.logging.info(f"Added Score from round {self.round} of {self._tournament.name} "
                                f"between {self.winner} and {self.loser} into the DB")
            self.id = cursor.lastrowid
            config.CON.commit()
        except (mysql.connector.IntegrityError, mysql.connector.DataError) as e:
            config.logging.error(f"Failed to add score from round {self.round} of {self._tournament.name} "
                                 f"between {self.winner} and {self.loser} into the DB")
        cursor.close()

    def _save_into_games_teams(self, team):
        cursor = config.CON.cursor()
        try:
            cursor.execute(''' insert into games_players (team_id, game_id, won)
                                values(%s, %s, %s)''',
                           [team.id, self.id,
                            self._win])
            config.logging.info(f"Added new row in games_players team_id:{team.id}, game_id:{self.id} "
                                f"between {self.winner} and {self.loser} into the DB")
            config.CON.commit()
        except (mysql.connector.IntegrityError, mysql.connector.DataError) as e:
            config.logging.error(f"Failed to add new row in games_players team_id:{team.id}, game_id:{self.id}")

        cursor.close()

    def _save_into_games_players(self, player):
        cursor = config.CON.cursor()
        try:
            cursor.execute(''' insert into games_players (player_id, game_id, won)
                                values(%s, %s, %s)''',
                           [player.id, self.id,
                            self._win])
            config.logging.info(f"Added new row in games_players player_id:{player.id}, game_id:{self.id} "
                                f"between {self.winner} and {self.loser} into the DB")
            config.CON.commit()
        except (mysql.connector.IntegrityError, mysql.connector.DataError) as e:
            config.logging.error(f"Failed to add new row in games_players player_id:{player.id}, game_id:{self.id}"
                                 f" into the games_players table")
        cursor.close()

    def _save_into_database(self, player=None, team=None):
        # Input data into players table if needed
        if team:
            if team.check_exist():  # IN DB
                team.get_from_table()
            else:  # not in DB
                team.save_into_table()
            # Into game_players
            self._save_into_games_teams(team)
        else:
            if player.check_player_exist(): # IN DB
                player.get_from_table()
            else: # not in DB
                player.save_into_table()
            # Into game_players
            self._save_into_games_players(player)

    def scrape_tournament_teams(self):
        """ Extract tournament scores when it's a team tournament """
        driver = webdriver.Chrome(config.PATH)
        driver.get(self.url)
        self._driver = driver

        draws = self._driver.find_element_by_link_text('DRAWS')
        draw_page = draws.get_attribute('href')
        self._driver.close()

        driver = webdriver.Chrome(config.PATH)
        driver.get(draw_page)
        self._driver = driver
        table = self._driver.find_element_by_class_name('atpcup-draw')
        rounds = table.find_elements_by_class_name('tie-container')
        for round in rounds:
            self.reset()
            round_list = round.text.split()
            team1 = round_list[0]
            team2 = round_list[2]
            self.teams.append(team1)
            self.teams.append(team2)
            team1_score = int(round_list[1])
            team2_score = int(round_list[3])
            self.round = round.find_element_by_tag_name('h3').get_attribute('innerText')
            self.score = ''.join(str(team1_score) + '-' + str(team2_score))
            if team1_score > team2_score:
                self.winner = team1
                self.loser = team2
            else:
                self.winner = team2
                self.loser = team1

            config.logging.info(f"Scrapping match round- {self.round}between {self.winner} and {self.loser}")

            #save if game doesn't exist
            if not self._check_game_exist_teams():
                self._save_into_games()

                for team in self.teams:
                    new_team = AtpTeam(team)
                    if team == self.winner:
                        self._win = True
                    else:
                        self._win = False

                    # Save into games_players and teams
                    self._save_into_database(team=new_team)

        self._driver.close()

    def scores_tournament_doubles(self, test=False):
        """ Extract Double's scores from tournament """
        driver = webdriver.Chrome(config.PATH)
        driver.get(self.doubles_scores_url)
        self._driver = driver
        table = self._driver.find_element_by_class_name('day-table')
        tbody = table.find_elements_by_tag_name('tbody')
        thead = table.find_elements_by_tag_name('thead')
        for head, body in zip(thead, tbody):
            self._set_round(head)
            tr_l = body.find_elements_by_tag_name('tr')

            for tr in tr_l:
                self.reset()
                self._set_scores_info_doubles(tr)
                config.logging.info(f"Scrapping {self.round} between {self.winner} and {self.loser}")

                # Save into games
                if self._check_game_exist(): break
                self._save_into_games()

                for url_player in self.url_players:
                    player = AtpPlayer(url_player[0]).get_player_info()
                    self._win = url_player[1]
                    self._save_into_database(player=player)
                if test: break

        # Close driver
        self._driver.close()

    def scores_tournament_data(self, test=False):
        """
        Extract general information about tournament of a particular year from ATP
        """
        driver = webdriver.Chrome(config.PATH)
        driver.get(self.url)
        self.doubles_scores_url = self.url+'?matchType=doubles' # url for double's scores
        self._driver = driver
        table = self._driver.find_element_by_class_name('day-table')
        tbody = table.find_elements_by_tag_name('tbody')
        thead = table.find_elements_by_tag_name('thead')
        for head, body in zip(thead, tbody):
            self._set_round(head)
            tr_l = body.find_elements_by_tag_name('tr')

            for tr in tr_l:
                self.reset()
                self._set_scores_info(tr)
                config.logging.info(f"Scrapping {self.round} between {self.winner} and {self.loser}")

                # Save into games
                if self._check_game_exist(): break
                self._save_into_games()

                # Get data of the last meeting between these two players through an API call
                try:
                    api = API()
                    api.last_meeting(self.winner, self.loser, self.id)
                except ValueError as v:
                    config.logging.error(f"ERROR- {v}. could not get players {self.winner} and "
                                         f"{self.loser}'s last meeting.")
                except Exception:
                    config.logging.error(f"ERROR- could not get players {self.winner} and "
                                         f"{self.loser}'s last meeting.")

                # Save into games_players and players
                for url_player in self.url_players:
                    player = AtpPlayer(url_player[0]).get_player_info()
                    self._win = url_player[1]
                    self._save_into_database(player=player)
                if test: break
        # Close driver
        self._driver.close()

        # Get double's scores
        self.scores_tournament_doubles()


class AtpTeam:
    def __init__(self, team_name):
        self.id = None
        self.name = team_name

    def get_from_table(self):
        """ Get team id from the teams table."""
        cursor = config.CON.cursor()
        cursor.execute("select team_id from teams where name = %s ", [self.name])
        self.id = cursor.fetchall()[0][0]
        config.logging.info(f'Got id of team {self.name}')
        cursor.close()

    def save_into_table(self):
        cursor = config.CON.cursor()
        try:
            cursor.execute(''' insert into teams (name) values (%s) ''',
                           [self.name])
            config.logging.info(f"Added {self.name} into the DB")
            self.id = cursor.lastrowid
            config.CON.commit()
        except (mysql.connector.IntegrityError, mysql.connector.DataError) as e:
            config.logging.error(
                f"Failed to enter team {self.name} details into the DB- {e}")
            self.id = None
        cursor.close()

    def check_champ_exists(self, tourn_id):
        cursor = config.CON.cursor()
        cursor.execute("select team_id from champions where team_id = %s "
                       "and tournament_id = %s ", [self.id, tourn_id])
        check_exists = cursor.fetchall()

        if len(check_exists) > 0:
            config.logging.info(f'Tournament {tourn_id} and winner {self.name} already exist in DB')
            cursor.close()
            return True
        else:
            cursor.close()
            return False

    def check_exist(self):
        """ Check if team exists in db. """

        # check if player exists in the DB
        cursor = config.CON.cursor()
        cursor.execute("select team_id from teams where name = %s ", [self.name])
        check_exist = cursor.fetchall()
        if len(check_exist) > 0:  # Team exists in db
            config.logging.info(f"Team {self.name} already exists in teams table.")
            self.id = check_exist[0][0]
            cursor.close()
            return True
        else:
            cursor.close()
            return False


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
        self.id = None

    def get_from_table(self):
        """ Get player id from the player table."""
        cursor = config.CON.cursor()
        cursor.execute("select player_id from players where first_name = %s "
                       "and last_name = %s ", [self.firstname, self.lastname])
        self.id = cursor.fetchall()[0][0]
        cursor.close()

    def save_into_table(self):
        cursor = config.CON.cursor()
        try:
            cursor.execute(''' insert into players (first_name,last_name,ranking_DBL,ranking_SGL,
                        career_high_DBL,career_high_SGL,turned_pro, weight,height, total_prize_money, country, birth)
                        values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ''',
                           [self.firstname, self.lastname,
                            self.ranking_dbl, self.ranking_sgl, self.career_high_dbl,
                            self.career_high_sgl, self.turned_pro, self.weight, self.height,
                            self.total_prize_money, self.country, self.date_birth])
            config.logging.info(f"Added {self.firstname} {self.lastname} into the DB")
            self.id = cursor.lastrowid
            config.CON.commit()
        except (mysql.connector.IntegrityError, mysql.connector.DataError) as e:
            config.logging.error(
                f"Failed to enter player {self.firstname} {self.lastname} details into the DB- {e}")
            self.id = None
        cursor.close()

    def check_champ_exists(self, tourn_id):
        cursor = config.CON.cursor()
        cursor.execute("select player_id from champions where player_id = %s "
                       "and tournament_id = %s ", [self.id, tourn_id])
        check_exists = cursor.fetchall()

        if len(check_exists) > 0:
            config.logging.info(f'Tournament {tourn_id} and player {self.firstname} already exists in DB')
            cursor.close()
            return True
        else:
            cursor.close()
            return False

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
            self.id = check_exist[0][0]
            cursor.close()
            return True
        else:
            cursor.close()
            return False

    def _set_player_ranking(self):
        try:
            self.ranking_sgl = int(self._driver.find_elements_by_class_name('stat-value')[0].get_attribute(
                'data-singles'))  # current ranking- singles
            self.ranking_dbl = int(self._driver.find_elements_by_class_name('stat-value')[0].get_attribute(
                'data-doubles'))  # current ranking- doubles
        except Exception:
            self.ranking_sgl = None
            self.ranking_dbl = None
            config.logging.warning("couldn't find player's singles/doubles ranking..")

    def _set_player_highest_ranking(self):
        self.career_high_sgl = int(self._driver.find_elements_by_class_name('stat-value')[5].get_attribute(
            'data-singles'))  # career high ranking- singles
        self.career_high_dbl = int(self._driver.find_elements_by_class_name('stat-value')[5].get_attribute(
            'data-doubles'))  # career high ranking- doubles

    def _set_player_country(self):
        try:
            self.country = self._driver.find_element_by_class_name('player-flag-code').text  # country
        except Exception:
            self.country = None
            config.logging.warning("couldn't find player's country..")

    def _set_player_datebirth(self):
        try:
            self.date_birth = self._driver.find_element_by_class_name('table-birthday').text.strip('()')  # date of birth
        except Exception:
            self.date_birth = None
            config.logging.warning("couldn't find player's date of birth..")

    def _set_player_turnedpro(self):
        try:
            self.turned_pro = int(self._driver.find_elements_by_class_name('table-big-value')[1].text)  # turned pro
        except Exception:
            self.turned_pro = None
            config.logging.warning("couldn't find the date the player turned pro..")

    def _set_player_weight_height(self):
        try:
            self.weight = float(self._driver.find_element_by_class_name('table-weight-lbs').text)  # weight

            self.height = float(self._driver.find_element_by_class_name('table-height-cm-wrapper').text[1:4])  # height
        except Exception:
            self.weight = None
            self.height = None
            config.logging.warning("couldn't find player's height\weight..")

    def _set_player_total_prize(self):
        try:
            self.total_prize_money = int(
                self._driver.find_elements_by_class_name('stat-value')[8].text.split()[0][1:].replace(',',                                                                                        ''))  # total prize money
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

        config.logging.info("Getting info about {} {}".format(self.firstname, self.lastname))
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
        self.url_score = None
        self.single_winner = None
        self.double_winner = None
        self.team_winner = None
        self._driver = None
        self._url_winner = list()
        self.players = None
        self.id = None
        self.type = None
        self._score = None

    def reset(self):
        """ Reset the object keeping _driver, year and tournament_type """
        self.location = None
        self.date = None
        self.name = None
        self.draw_singles = None
        self.draw_doubles= None
        self.surface = None
        self.prize_money = None
        self.url_score = None
        self.single_winner = None
        self.double_winner = None
        self.team_winner = None
        self._url_winner = list()
        self.id = None
        self.type = None

    def _connexion(self, url):
        """ return a selenium object containing the page of the input url."""
        # user_agent = config.USER_AGENT
        # options = webdriver.ChromeOptions()
        # options.headless = True
        # options.add_argument(f'user-agent={user_agent}')
        # options.add_argument("--window-size=1280,800")
        # options.add_argument('--ignore-certificate-errors')
        # options.add_argument('--allow-running-insecure-content')
        # options.add_argument("--disable-extensions")
        # options.add_argument("--proxy-server='direct://'")
        # options.add_argument("--proxy-bypass-list=*")
        # options.add_argument("--start-maximized")
        # options.add_argument('--disable-gpu')
        # options.add_argument('--disable-dev-shm-usage')
        # options.add_argument('--no-sandbox')
        # options.add_argument('--disable-blink-features=AutomationControlled')
        # driver = webdriver.Chrome(executable_path=config.PATH, options=options)
        driver = webdriver.Chrome(config.PATH)
        driver.get(url)
        year = re.findall(r'year=([0-9]{4})', url)[0]
        self.year = year
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
            self.url_score = selenium_object.find_element_by_class_name('button-border').get_attribute('href')
        except common.exceptions.NoSuchElementException:
            self.url_score = 'NA'

    def _set_winner(self, selenium_object):
        """ Set winner from selenium object - (tourney-detail-winner)"""
        winners = selenium_object.find_elements_by_class_name('tourney-detail-winner') # winners
        self._url_winner = []
        # get the tournament winners:
        for winner in winners:
            if 'SGL: ' in winner.text:
                self.single_winner = winner.text.split(': ')[1]
                self._url_winner.append((winner.find_element_by_tag_name('a').get_attribute('href'), 'SGL'))
            elif 'DBL: ' in winner.text:
                self.double_winner = winner.text.split(': ')[1]
                self._url_winner.append((winner.find_elements_by_tag_name('a')[0].get_attribute('href'), 'DBL'))
                self._url_winner.append((winner.find_elements_by_tag_name('a')[1].get_attribute('href'), 'DBL'))
                self.type = 'DBL'
            else:  # In case of team winner
                self.team_winner = winner.text.split(': ')[1]
                self.type = 'Team'

    def _save_into_table_champion(self, player=None, team=None):
        cursor = config.CON.cursor()
        if player:
            champ_exists = player.check_champ_exists(self.id)
            if not champ_exists:
                try:
                    cursor.execute(''' insert into champions (player_id,tournament_id,team_id,type) 
                                    values(%s,%s,%s,%s)''',
                                   [player.id, self.id, None,
                                    self.type])
                    config.logging.info(f"Updated champions table successfully!")
                except (mysql.connector.IntegrityError, mysql.connector.DataError) as e:
                    config.logging.error(f'Error when trying to update champions for - {self.name}: {e}')
            else:
                config.logging.info(f'Player {player.firstname} {player.lastname} '
                                    f'already saved as the winner of tournament {self.name}.')
            config.CON.commit()
            cursor.close()

        elif team:
            champ_exists = team.check_champ_exists(self.id)
            if not champ_exists:
                try:
                    cursor.execute(''' insert into champions (team_id,tournament_id,player_id,type) 
                                    values(%s,%s,%s,%s)''',
                                   [team.id, self.id, None,
                                    self.type])
                    config.logging.info(f"Updated champions table successfully!")
                except (mysql.connector.IntegrityError, mysql.connector.DataError) as e:
                    config.logging.error(f'Error when trying to update champions for - {self.name}: {e}')
            else:
                config.logging.info(f'Team {team.name} already saved as the winner in tournament {self.name}.')
            config.CON.commit()
            cursor.close()

    def _save_into_table(self):
        """  Save tournament information into the tournament table"""
        cursor = config.CON.cursor()
        try:
            cursor.execute(''' insert into tournaments (year,type,name,location,date,SGL_draw,
                DBL_draw, surface, prize_money) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                           [self.year, self.new_tourn_type,
                            self.name, self.location, self.dates,
                            self.draw_singles,
                            self.draw_doubles,
                            self.surface, self.prize_money])
            self.id = cursor.lastrowid
            config.logging.info(f"Scraped tournament {self.name} - {self.year} and updated DB successfully!")
        except (mysql.connector.IntegrityError, mysql.connector.DataError) as e:
            config.logging.error(f'Error when trying to insert tournament- {self.name}: {e}')
        config.CON.commit()
        cursor.close()

    def _save_into_database(self, player=None, team=None):
        """Save all information scrapped in the database."""
        if player:
            check_exist = player.check_player_exist()
            # Save player's information
            if (self.players) & (check_exist is False):  # player is not in DB
                player.save_into_table()
                self._save_into_table_champion(player=player)
            elif (self.players) & (check_exist):  # Player is already in db
                player.get_from_table()
                self._save_into_table_champion(player=player)
        elif team:
            check_exist = team.check_exist()
            # Save Team's information
            if (self.players) & (check_exist is False):  # Team is not in DB
                team.save_into_table()
                self._save_into_table_champion(team=team)
            elif (self.players) & (check_exist):  # Team is already in db
                team.get_from_table()
                self._save_into_table_champion(team=team)

    def _check_tournament_exist(self):
        """ check if tournament exists in DB  """
        cursor = config.CON.cursor()
        cursor.execute("select tournament_id from tournaments where name = %s "
                       "and year = %s ", [self.name, self.year])  # check if tournament exist in DB,
        check_exist = cursor.fetchall()
        cursor.close()
        if len(check_exist) > 0:  # if tournament does exist
            config.logging.info(f'''This tournament: {self.name} - {self.year} was already scraped before, and is '
                                        already located in the DB''')
            self.id = check_exist[0][0]

            return True

    def tournament_data(self, url, score=None, winner=None, test=False):
        """Go through the url page, get information on each tournament and save them in tournament table inside
        web_scraping_project db
        url - url to scrap
        score = if True scrap all scores of each tournament
        players - if 'winner' scrap information about winners of each tournament.
                  if 'all' scrap information about each player of the tournament
                """
        self.players = winner
        self._score = score
        self._connexion(url)
        table = self._driver.find_element_by_id('scoresResultsArchive')
        tr = table.find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')
        config.logging.info(f'Scraping results from year {url}. scraping {filter} tournaments.')

        # each 'tr' tag holds the relevant information regarding each tournament in the URL
        for count, i in enumerate(tr):
            self.reset()
            if self.new_tourn_type is None:
                self._set_tournament_type(i)  # Tournament Type
            self._set_tournament_title_content(i)  # Set name, location, dates from title-content

            # Check if tournament exists in db:
            config.logging.info(f'Scraping tournament of type: {self.new_tourn_type}')
            self._set_tournament_detail(i)  # Set draw, single, double, surface and prize_money
            self._set_url_scores(i)  # Set url of tournament scores
            self._set_winner(i)  # Set winner_single, and winner_double, if they exist
            # Save tournament information if needed
            if not self._check_tournament_exist():
                self._save_into_table()
            if winner:
                if self.type == 'Team':# In case of team winner- there will be only team winner and no singles/ doubles
                    team = AtpTeam(self.team_winner)
                    self._save_into_database(team=team)
                else:
                    for url in self._url_winner:  # len()=1 : One single winner, len()=3 : Single and double winners
                        self.type = url[1]
                        player = AtpPlayer(url[0]).get_player_info()
                        config.logging.info(f"New player {player.lastname} {player.firstname}")
                        self._save_into_database(player=player)
            if score:
                if self.type == 'Team':
                    atpscore = AtpScores(self)
                    atpscore.scrape_tournament_teams()
                else:
                    atpscore = AtpScores(self)
                    atpscore.scores_tournament_data()
            if test: break
        self._driver.close()
        config.logging.info(f'Finished scraping {url}')







