import mysql.connector
import logging
import http.client

# SQL connector and selenium path
CON = mysql.connector.connect(port='<PORT>', user='<USER>', password='<PASSWORD>', db='<DB>')
PATH = 'C:\Program Files\chromedriver.exe' # For Windows
# PATH = '/usr/bin/chromedriver' # For Linux

# USER_AGENT = """Mozilla/5.0 (Windows NT 10.0; Win64; x64)
#  AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"""

# Logging configurations
logging.basicConfig(filename='web_scraping_project.log',
                    format='%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s',
                    level=logging.INFO)

# API configurations
api_conn = http.client.HTTPSConnection("api.sportradar.us")
api_conn2 = http.client.HTTPSConnection("api.sportradar.us")

# API key:
API_KEY = '<YOUR-API-KEY>'


def connect(conn):
    conn.request("GET",
                 f"https://api.sportradar.com/tennis-t2/en/players/rankings.json?api_key={API_KEY}")


def connect2(conn, player_id, player_id2):
    conn.request("GET",
              f"/tennis-t2/en/players/sr:competitor:{player_id}"
              f"/versus/sr:competitor:{player_id2}/matches.json?api_key={API_KEY}")

