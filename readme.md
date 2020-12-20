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
* Can download relevant dependencies using existing requirement.txt file:
    ```bash
    pip install -r requirements.txt
    ```

## Usage
Scraper usage :

    python main.py <start_year> <end_year> <filter> --winner --score

Example- to scrape atpgs tournaments between
2010 and 2015 with all of the champions information, we'll use :

    python main.py 2010 2015 -w
      
    
Where filter is the type of tournament to scrap. It can take :
* atpgs - ATP Tour & Grand Slams. (default)
* gs - Grand Slams.
* atp - search only atp tournaments.
* 1000 - atp1000.
* ch - ATP Challenger Tour.
* fu - ITF Future.
* XXI - XXI.

With options:
* -w : scrap champions information.
* -s : scrap score of each match in tournament and information about each player.

API usage :

There is also an option to use API calls in order to enrich the dataset even more
 (via https://developer.sportradar.com/ API). Using this service the scrapper adds data regarding the last
 meeting of two opponents.
 <br>
 This data relates only to active players.
 
 * To use the api, go to this link: https://developer.sportradar.com/docs/read/Home#getting-started and get 
 an API key for the tennis-vs services. Paste your API key in the config file. 
 