# ATP Scraper

ATP Scraper is a Python program for scraping data from the ATP website, https://www.atptour.com/, and save it in a mysql database.

## Installation

1. Download scripts from: https://github.com/talbaram3192/web_scraping_project. 
2. Create and load prexisting database
    ```bash
    mysql -u root -p -t < create_db_tables.sql
    ```
3. Adapt the 'config.py' to your environment. Put your chromedriver.exe or bin path to PATH. Put your sql parameters in 
MYSQL_PARAMS.
   
## Requirement

To use this scraper you must have :
* ChromeDriver installed. 
If not, go to https://chromedriver.chromium.org/getting-started.
* MySQL server installed. If not, go to https://dev.mysql.com/doc/mysql-installation-excerpt/5.7/en/.
* Can download relevant dependencies using existing ruquirements.txt file:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

From the folder containing ATP scraper, for instance to scrape atp500 tournaments between
2010 and 2015 :

    python main.py 2010 2015 500 
    
Scraper usage :

    python main.py start_year end_year filter
    

Where filter is the type of tournament to scrap. It can take :
* all - search all tournaments.
* 250 - search only atp250 tournaments.
* 500 - search only atp500 tournaments.
* 1000 - search only atp1000 tournaments.
* grandslam - search only grand slam tournaments.

