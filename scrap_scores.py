import os
from selenium import webdriver, common
from selenium.webdriver.common.keys import Keys
import time
import csv
import datetime
import sys

# https://www.atptour.com/en/scores/archive/chengdu/7581/2018/results

COLUMNS = ['id_tournament', 'name', 'year', 'url', 'rounds',
           'loser', 'winner', 'scores', 'url_detail', 'url_winner',
           'url_loser', 'URL_check']

PATH_CSV = '/home/choukroung/PycharmProjects/itc/pythonProject/web_scraping_project/' \
           'archive/tournaments_data_6112020.csv'
PATH_TEST = '/home/choukroung/PycharmProjects/itc/pythonProject/web_scraping_project/' \
            'archive/test_empty.csv'
PATH = '/usr/bin/chromedriver'


def check_header(header):
    """ Check if header of the imported csv are in the right places : Year, Name, ...., URL"""
    try:
        assert header[0] == 'Year'
        assert header[1] == 'Name'
        assert header[-1] == 'URL_Tournament'
    except AssertionError:
        print('Wrong format of csv. Exit.')
        sys.exit(1)


def get_urls(path=PATH_CSV):
    """ read all relevant URLS from the a csv of data extracted from ATP website and return a list of them """
    if not os.path.exists(path):
        print('Tournament csv file is not found. Cannot get urls. Exit')
        sys.exit(1)
    else:
        with open(path, newline='') as csvfile:
            atpreader = csv.reader(csvfile, delimiter=',')
            atp_infos = []
            urls = []
            check_header(next(atpreader))
            for row in atpreader:
                # Getting Year, Name  and Url of the tournament
                atp_infos.append([row[0], row[1], row[-1]])
        return atp_infos


def scores_tournament_data(atp_info, name='tournament_scores', test=False):
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
    # Formatting the name of csv
    today = datetime.date.today().strftime('%d%m%Y')
    filename = "tournaments_scores_data_" + today + '.csv'
    # Check if csv exists
    header = os.path.exists(filename)
    #
    with open(filename, 'a') as csv_file:
        writer = csv.writer(csv_file)
        # Check if the file is empty. If so, we write the header.
        if not header: writer.writerow(COLUMNS)
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
    if test:
        print('Test. Exit')
    #    print('Time:{}s'.format(time.time() - start_time))
        sys.exit(1)
    print("URL - {} - treated with : {} KO".format(url, KO_count))
    return atp_table


def extract_scores(path= PATH_CSV, name='tournament_scores'):
    # Get urls and some other information from tournament csv file
    atp_infos = get_urls(path)[3930:]
    # Extract data from atp selected urls and write them in a csv
    # 180 + 80 + 639 + 2757 + 273

    atp_table = []
    for i, atp_info in enumerate(atp_infos):
        atp_table.append(scores_tournament_data(atp_info))
        print("{} batch out of {}".format(i, len(atp_infos)))
