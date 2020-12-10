import mysql.connector
import logging
import http.client

# CON = mysql.connector.connect(port='3306', user='root', password='sampras1', db='web_scraping_project')
CON = mysql.connector.connect(port='3307', user='root', password='Twtcmss2954455', db='web_scraping_project')

PATH = 'C:\Program Files\chromedriver.exe' # For Windows
# PATH = '/usr/bin/chromedriver' # For Linux


# Logging configurations
logging.basicConfig(filename='web_scraping_project.log',
                    format='%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s',
                    level=logging.INFO)

# API configurations
api_conn = http.client.HTTPSConnection("api.sportradar.us")


def connect(conn):
    conn.request("GET", "https://api.sportradar.com/tennis-t"
                            "2/en/players/rankings.json?api_key=fejr9a3y47v6m574vf8ezgyd")

# api_conn2.request("GET",
#               f"/tennis-t2/en/players/sr:competitor:%s"
#               f"/versus/sr:competitor:%s/matches.json?api_key=fejr9a3y47v6m574vf8ezgyd")
