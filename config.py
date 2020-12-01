import mysql.connector
import logging

# MYSQL_PARAMS = {port='3307', 'user'='root', 'password'='Twtcmss2954455', 'db'='web_scraping_project'}
CON = mysql.connector.connect(port='3307', user='root', password='Twtcmss2954455', db='web_scraping_project')
PATH = 'C:\Program Files\chromedriver.exe' # For Windows
# PATH = '/usr/bin/chromedriver' # For Linux

logging.basicConfig(filename='web_scraping_project.log',
                    format='%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s',
                    level=logging.INFO)