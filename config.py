import mysql.connector
import logging
import http.client

# SQL connector and selenium path
CON = mysql.connector.connect(port='3307', user='root', password='Twtcmss2954455', db='web_scraping_project')
PATH = 'C:\Program Files\chromedriver.exe' # For Windows
# PATH = '/usr/bin/chromedriver' # For Linux

# Logging configurations
logging.basicConfig(filename='web_scraping_project.log',
                    format='%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s',
                    level=logging.INFO)

# API configurations
api_conn = http.client.HTTPSConnection("api.sportradar.us")
api_conn2 = http.client.HTTPSConnection("api.sportradar.us")

# Official API key here. Uncomment in order to use
# API_KEY = 'fxrpme5netttrsrbqfde6pmr'
API_KEY = 'running_without_api'


def connect(conn):
    conn.request("GET",
                 f"https://api.sportradar.com/tennis-t2/en/players/rankings.json?api_key={API_KEY}")


def connect2(conn, player_id, player_id2):
    conn.request("GET",
              f"/tennis-t2/en/players/sr:competitor:{player_id}"
              f"/versus/sr:competitor:{player_id2}/matches.json?api_key={API_KEY}")

