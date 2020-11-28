
from selenium import webdriver, common
import config
import mysql.connector


def get_players_info(player_url):
    """ Get players information from their profiles """

    #TODO upload to champions table

    first = player_url.split('/')[5].split('-')[0]
    last = player_url.split('/')[5].split('-')[1]

    # check if player exists in the DB
    cursor = config.CON.cursor()
    cursor.execute("select * from players where first_name = %s "
                   "and last_name = %s ", [first, last])
    check_exist = cursor.fetchall()
    if len(check_exist) == 0 and first != 'NA':  # if player doesnt exist in DB but has details in the website
        config.logging.info(f"Scraping {first} {last}")

        driver = webdriver.Chrome(config.PATH)
        driver.get(player_url)

        try:
            ranking_sgl = int(driver.find_elements_by_class_name('stat-value')[0].get_attribute('data-singles'))  # current ranking- singles
            print(ranking_sgl)
            ranking_dbl = int(driver.find_elements_by_class_name('stat-value')[0].get_attribute('data-doubles'))  # current ranking- doubles
            print(ranking_dbl)
        except Exception:
            ranking_sgl = None
            ranking_dbl = None
            config.logging.warning("couldn't find player's singles/doubles ranking..")

        career_high_sgl = int(driver.find_elements_by_class_name('stat-value')[5].get_attribute('data-singles')) # career high ranking- singles
        print(career_high_sgl)
        career_high_dbl = int(driver.find_elements_by_class_name('stat-value')[5].get_attribute('data-doubles'))  # career high ranking- doubles
        print(career_high_dbl)

        try:
            country = driver.find_element_by_class_name('player-flag-code').text # country
            print(country)
        except Exception:
            country = None
            config.logging.warning("couldn't find player's country..")

        try:
            date_birth = driver.find_element_by_class_name('table-birthday').text.strip('()')  # date of birth
            print(date_birth)
        except Exception:
            date_birth = None
            config.logging.warning("couldn't find player's date of birth..")
        try:
            turned_pro = int(driver.find_elements_by_class_name('table-big-value')[1].text) # turned pro
            print(turned_pro)
        except Exception:
            turned_pro = None
            config.logging.warning("couldn't find the date the player turned pro..")
        try:
            weight = float(driver.find_element_by_class_name('table-weight-lbs').text)  # weight
            print(weight)

            height = float(driver.find_element_by_class_name('table-height-cm-wrapper').text[1:4])  # height
            print(height)
        except Exception:
            weight = None
            height = None
            config.logging.warning("couldn't find player's height\weight country..")
        try:
            total_prize_money = int(driver.find_elements_by_class_name('stat-value')[8].text.split()[0][1:].replace(',', '')) # total prize money
            print(total_prize_money)
        except Exception:
            total_prize_money = None
            config.logging.warning("couldn't find player's total prize money earnings..")


        try:
            cursor.execute(''' insert into players (first_name,last_name,ranking_DBL,ranking_SGL,
            career_high_DBL,career_high_SGL,turned_pro, weight,height, total_prize_money, country, birth)
            values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ''',
                           [first, last,
                            ranking_dbl, ranking_sgl, career_high_dbl,
                            career_high_sgl, turned_pro, weight, height,
                            total_prize_money, country, date_birth])
            config.logging.info(f"Added {first} {last} into the DB")
            config.CON.commit()
        except (mysql.connector.IntegrityError, mysql.connector.DataError) as e:
            config.logging.error(f"Failed to enter player's details into the DB- {e}")

        driver.close()
