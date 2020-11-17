
import main
from selenium import webdriver, common


def get_players_info(players):
    """ Get players information from their profiles """
    for url in players:
        driver = webdriver.Chrome(main.PATH)
        driver.get(url)
        try:
            first = driver.find_element_by_class_name('first-name').text
            print(first)

            last = driver.find_element_by_class_name('last-name').text
            print(last)

            ranking_sgl = driver.find_elements_by_class_name('stat-value')[0].get_attribute('data-singles')  # current ranking- singles
            print(ranking_sgl)
            ranking_dbl = driver.find_elements_by_class_name('stat-value')[0].get_attribute('data-doubles')  # current ranking- doubles
            print(ranking_dbl)

            career_high_sgl = driver.find_elements_by_class_name('stat-value')[5].get_attribute('data-singles') # career high ranking- singles
            print(career_high_sgl)
            career_high_dbl = driver.find_elements_by_class_name('stat-value')[5].get_attribute('data-doubles')  # career high ranking- doubles
            print(career_high_dbl)

            country = driver.find_element_by_class_name('player-flag-code').text # country
            print(country)

            date_birth = driver.find_element_by_class_name('table-birthday').text.strip('()')  # date of birth
            print(date_birth)

            turned_pro = driver.find_elements_by_class_name('table-big-value')[1].text # turned pro
            print(turned_pro)

            weight = driver.find_element_by_class_name('table-weight-lbs').text  # weight
            print(weight)

            height = driver.find_element_by_class_name('table-height-ft').text  # height
            print(height)

            total_prize_money = driver.find_elements_by_class_name('stat-value')[8].text.split()[0] # total prize money
            print(total_prize_money)

        except IndexError:
            pass
        except common.exceptions.NoSuchElementException:
            pass
        except:
            pass

        driver.close()